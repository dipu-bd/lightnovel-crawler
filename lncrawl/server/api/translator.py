"""Admin-only reverse proxy to the internal translator service dashboard/config API.

The service runs unpublished on the docker network; this proxy is the only way in and
authorizes every request as admin. Auth is a Bearer header, a `?token=` query param, or a
path-scoped cookie — the query/cookie forms let the dashboard work under plain browser
navigation, where fetches can't set headers.

The dashboard's assets and API calls are all relative URLs, so a single injected
`<base href>` (mirroring the browse middleware) resolves them under the proxy prefix — no
per-route URL rewriting. `X-Forwarded-Prefix` lets the service prefix its own docs/OpenAPI
links too.
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


def _inject_base(html: str) -> str:
    """Anchor the page's relative URLs at the proxy prefix. Skipped if the service
    already sets its own base."""
    if "<base" in html:
        return html
    return html.replace("<head>", f'<head><base href="{_PREFIX}/">', 1)


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

    # Forward the full prefixed path so the service can strip it via root_path
    # (set from the X-Forwarded-Prefix below); keeps its static mount and docs working.
    target = f"{ctx.config.translator.api_url}{_PREFIX}/{path}"
    body = await request.body()
    fwd_headers: Dict[str, str] = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() not in ("authorization", "cookie")
    }
    fwd_headers["X-Forwarded-Prefix"] = _PREFIX

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
    if "text/html" in ctype:
        content = _inject_base(content.decode(resp.encoding or "utf-8", errors="replace")).encode()

    out_headers = {k: v for k, v in resp.headers.items() if k.lower() not in _HOP_BY_HOP}
    out = Response(content, resp.status_code, out_headers, media_type=ctype or None)
    if from_query:
        # Non-GET with ?token= (GET redirects above): cookie it for follow-ups.
        out.set_cookie(_COOKIE, token, httponly=True, samesite="strict", path=_PREFIX)
    return out
