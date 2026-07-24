"""Admin-only gate for the embedded translator dashboard/config API.

The translator runs in-process (`ctx.translator.engine`); its dashboard app is
mounted under this ASGI wrapper, which authorizes every request as admin. Auth
is a Bearer header, a `?token=` query param, or a path-scoped cookie — the
query/cookie forms let the dashboard work under plain browser navigation,
where fetches can't set headers.

The dashboard's assets and API calls are all relative URLs, so they resolve
under the mount prefix as long as the shell URL keeps its trailing slash —
the gate redirects the bare prefix to enforce that.
"""

import logging
from typing import Optional, Tuple
from urllib.parse import urlencode

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ...context import ctx
from ...dao.user import User, UserRole

logger = logging.getLogger(__name__)

_PREFIX = "/api/translator"
_COOKIE = "lncrawl_translator"


def _extract_token(request: Request) -> Tuple[Optional[str], bool]:
    """Return (token, from_query); from_query drives the cookie set on success."""
    auth = request.headers.get("Authorization", "")
    if auth[:7].lower() == "bearer ":
        return auth[7:].strip(), False
    query_token = request.query_params.get("token")
    if query_token:
        return query_token, True
    return request.cookies.get(_COOKIE), False


def _authorize(request: Request) -> Tuple[Optional[Response], Optional[str], bool]:
    """(error response, token, from_query). Errors are returned, not raised:
    the app-level exception handlers do not apply inside a raw ASGI mount."""
    token, from_query = _extract_token(request)
    if not token:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401), None, False
    try:
        user: User = ctx.users.verify_token(token, [UserRole.ADMIN])
        if user.role != UserRole.ADMIN or not user.is_active:
            raise PermissionError
    except Exception:
        return JSONResponse({"detail": "Forbidden"}, status_code=403), None, False
    return None, token, from_query


def _clean_query(request: Request) -> str:
    """The query string without our token; it must never reach the sub-app."""
    params = [(k, v) for k, v in request.query_params.multi_items() if k != "token"]
    return urlencode(params)


class TranslatorDashboard:
    """ASGI wrapper mounted at the prefix: admin auth + token→cookie dance
    around the embedded translator's dashboard app (built lazily so the
    first request, not import time, constructs the engine)."""

    def __init__(self) -> None:
        self._app: Optional[ASGIApp] = None

    @property
    def app(self) -> ASGIApp:
        if self._app is None:
            dashboard: ASGIApp = ctx.translator.engine.create_app()
            self._app = dashboard
        return self._app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        # Starlette mounts keep the full path in scope and put the prefix in
        # root_path; branch on the mount-relative path.
        full_path: str = scope.get("path") or "/"
        root_path: str = scope.get("root_path") or ""
        path = full_path[len(root_path) :] or "/" if full_path.startswith(root_path) else full_path

        # Clears the credential; unauthenticated by design (the web app calls
        # it on logout, possibly with an already-expired token).
        if path == "/logout" and request.method == "POST":
            response = Response(status_code=204)
            response.delete_cookie(_COOKIE, path=_PREFIX, httponly=True, samesite="strict")
            await response(scope, receive, send)
            return

        error, token, from_query = _authorize(request)
        if error is not None:
            await error(scope, receive, send)
            return
        assert token is not None

        # Browser navigation: cookie the token and redirect to a clean URL so
        # it never lingers in the address bar or history; the redirect
        # re-authorizes via the cookie.
        if from_query and request.method == "GET":
            query = _clean_query(request)
            location = full_path + (f"?{query}" if query else "")
            redirect = RedirectResponse(location, status_code=302)
            redirect.set_cookie(_COOKIE, token, httponly=True, samesite="strict", path=_PREFIX)
            await redirect(scope, receive, send)
            return

        # Strip the token from the forwarded query; cookie it on the response
        # for follow-ups (non-GET calls that authenticated via ?token=).
        if from_query:
            scope["query_string"] = _clean_query(request).encode()
            cookie_value = f"{_COOKIE}={token}; HttpOnly; Path={_PREFIX}; SameSite=strict"

            async def send_with_cookie(message: Message) -> None:
                if message["type"] == "http.response.start":
                    MutableHeaders(scope=message).append("set-cookie", cookie_value)
                await send(message)

            await self.app(scope, receive, send_with_cookie)
            return

        await self.app(scope, receive, send)
