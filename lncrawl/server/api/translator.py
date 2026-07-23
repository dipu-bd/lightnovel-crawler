"""Admin-only reverse proxy to the internal translator service dashboard/config API.

The service runs unpublished on the docker network; this proxy is the only way in and
authorizes every request as admin. Auth is a Bearer header, a `?token=` query param, or a
path-scoped cookie — the query/cookie forms let the dashboard work under plain browser
navigation, where fetches can't set headers.

Responses are rewritten from the SPA's root-absolute URLs to the proxy prefix, coupling us
to the service's URL layout until it grows a base-path option.
"""

import logging
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response
import requests
from starlette.concurrency import run_in_threadpool

from ...context import ctx
from ...dao.user import User, UserRole
from ...exceptions import ServerErrors

logger = logging.getLogger(__name__)

router = APIRouter()

_PREFIX = "/api/translator"
_COOKIE = "lncrawl_translator"

# Service-owned root paths, rewritten to the proxy prefix in text responses.
_ROOT_TOKENS = (
    "/static",
    "/config",
    "/engines",
    "/providers",
    "/routing",
    "/detect",
    "/translate",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
)

# Text only; JSON (e.g. /config) passes through untouched.
_REWRITE_TYPES = ("text/html", "javascript", "text/css")

# Not relayed in either direction.
_HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-encoding",
    "content-length",
    "host",
}


def _extract_token(request: Request) -> Tuple[Optional[str], bool]:
    """Return (token, from_query); from_query drives the cookie set on success."""
    auth = request.headers.get("Authorization", "")
    if auth[:7].lower() == "bearer ":
        return auth[7:].strip(), False
    query_token = request.query_params.get("token")
    if query_token:
        return query_token, True
    return request.cookies.get(_COOKIE), False


def _authorize(request: Request) -> Tuple[str, bool]:
    token, from_query = _extract_token(request)
    if not token:
        raise ServerErrors.unauthorized
    user: User = ctx.users.verify_token(token, [UserRole.ADMIN])
    if user.role != UserRole.ADMIN or not user.is_active:
        raise ServerErrors.forbidden
    return token, from_query


def _rewrite(text: str) -> str:
    for token in _ROOT_TOKENS:
        text = text.replace(f'"{token}', f'"{_PREFIX}{token}')
        text = text.replace(f"'{token}", f"'{_PREFIX}{token}")
    return text


# Registered before the catch-all so it clears the cookie instead of being proxied.
# Unauthenticated: it only deletes a credential, and the web app calls it on logout.
@router.post("/logout", include_in_schema=False)
def logout() -> Response:
    resp = Response(status_code=204)
    resp.delete_cookie(_COOKIE, path=_PREFIX, httponly=True, samesite="strict")
    return resp


@router.api_route("/", methods=["GET"], include_in_schema=False)
@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def proxy(request: Request, path: str = "") -> Response:
    token, from_query = _authorize(request)

    # Our token must never reach the service.
    params = {k: v for k, v in request.query_params.items() if k != "token"}

    # Browser navigation: cookie the token and redirect to a clean URL so it never
    # lingers in the address bar or history; the redirect re-authorizes via the cookie.
    if from_query and request.method == "GET":
        clean_qs = urlencode(params)
        location = request.url.path + (f"?{clean_qs}" if clean_qs else "")
        redirect = RedirectResponse(location, status_code=302)
        redirect.set_cookie(_COOKIE, token, httponly=True, samesite="strict", path=_PREFIX)
        return redirect

    target = f"{ctx.config.translator.api_url}/{path}"
    body = await request.body()
    fwd_headers: Dict[str, str] = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() not in ("authorization", "cookie")
    }

    try:
        resp = await run_in_threadpool(
            lambda: requests.request(
                request.method,
                target,
                params=params,
                data=body or None,
                headers=fwd_headers,
                timeout=(15, 120),
                allow_redirects=False,
            )
        )
    except requests.RequestException as e:
        raise ServerErrors.translation_service_unavailable.with_extra(str(e)) from e

    content = resp.content
    ctype = resp.headers.get("Content-Type", "")
    if any(t in ctype for t in _REWRITE_TYPES):
        content = _rewrite(content.decode(resp.encoding or "utf-8", errors="replace")).encode()

    out_headers = {k: v for k, v in resp.headers.items() if k.lower() not in _HOP_BY_HOP}
    out = Response(content, resp.status_code, out_headers, media_type=ctype or None)
    if from_query:
        # Non-GET with ?token= (GET redirects above): cookie it for follow-ups.
        out.set_cookie(_COOKIE, token, httponly=True, samesite="strict", path=_PREFIX)
    return out
