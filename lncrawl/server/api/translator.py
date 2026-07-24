"""Admin-only gate for the embedded translator dashboard/config API.

The translator runs in-process (`ctx.translator.engine`); its dashboard app is
mounted under this ASGI wrapper. The web shell, static assets, and Swagger docs
are served publicly; every API route requires an admin Bearer token (the API is
what exposes provider keys and config).

The dashboard forwards the admin token itself: lncrawl-web loads it with the
token in the URL fragment, the dashboard's `api.js` reads it and sends it as a
Bearer header, and its OpenAPI (built with `auth=True`) declares the scheme so
the docs' Authorize button works. This wrapper only verifies the token and gates
the API routes.
"""

import logging
from typing import Optional

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from ...context import ctx
from ...dao.user import UserRole
from ...exceptions import ServerError, ServerErrors
from ..security import authenticate, basic_auth, bearer_auth

logger = logging.getLogger(__name__)

# GET paths served without auth: the app shell, its static bundle, and the
# Swagger/ReDoc docs (which render like lncrawl's, Authorize button included).
_PUBLIC_GET_PATHS = frozenset(
    {
        "/",
        "/docs",
        "/redoc",
        "/docs/oauth2-redirect",
        "/openapi.json",
    }
)


def _mount_relative_path(scope: Scope) -> str:
    """Starlette keeps the full path in scope and the mount prefix in root_path."""
    full_path: str = scope.get("path") or "/"
    root_path: str = scope.get("root_path") or ""
    if full_path.startswith(root_path):
        return full_path[len(root_path) :] or "/"
    return full_path


def _is_public(path: str, method: str) -> bool:
    """Static assets are loaded by the browser, which cannot send a header; the
    docs render like lncrawl's (Authorize button). Everything else is a gated API."""
    if method != "GET":
        return False
    return path.startswith("/static/") or path in _PUBLIC_GET_PATHS


async def _authorize(request: Request) -> Optional[Response]:
    try:
        basic = await basic_auth(request)
        bearer = await bearer_auth(request)
        user = authenticate(basic, bearer, [UserRole.ADMIN])
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
    except ServerError as err:
        return err.to_response()
    except Exception:
        logger.exception("Translator dashboard authorization failed")
        return ServerErrors.forbidden.to_response()
    return None


class TranslatorDashboard:
    def __init__(self) -> None:
        self._app: Optional[ASGIApp] = None

    @property
    def app(self) -> ASGIApp:
        if self._app is None:
            dashboard: ASGIApp = ctx.translator.engine.create_app(auth=True)
            self._app = dashboard
        return self._app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = _mount_relative_path(scope)
        method: str = scope.get("method", "GET")

        if not _is_public(path, method):
            error = await _authorize(Request(scope, receive))
            if error is not None:
                await error(scope, receive, send)
                return

        await self.app(scope, receive, send)
