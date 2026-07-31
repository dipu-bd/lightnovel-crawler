from __future__ import annotations

import base64
import logging
import pickle
from urllib.parse import urljoin, urlparse

from scraper import Scraper
from scraper.exceptions import Blocked
from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from ...assets.scripts import browser_intercept_script
from ...context import ctx
from ...utils import browse_helper as helper

logger = logging.getLogger(__name__)

_HOP_BY_HOP = frozenset(
    [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
        "location",
        "set-cookie",
        "content-security-policy",
        "content-security-policy-report-only",
    ]
)


class BrowserNavigation:
    """Middleware that intercepts /browse/* paths and serves generated HTML/JS content."""

    def __init__(self, app, prefix: str = "/browse") -> None:
        self.app = app
        self.prefix = prefix.rstrip("/")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope["path"]
        if not path.startswith(self.prefix + "/") and path != self.prefix:
            await self.app(scope, receive, send)
            return

        sub_path = path[len(self.prefix) :].lstrip("/")
        query = scope.get("query_string", b"").decode()
        if query:
            sub_path = f"{sub_path}?{query}"
        request = Request(scope, receive)
        response = await self.generate(sub_path, request)
        await response(scope, receive, send)

    async def generate(self, path: str, request: Request) -> Response:
        # `raise_for_status=False`: this middleware proxies whatever the origin says,
        # including a 4xx, and turning that into an exception would hide the status the
        # browser needs to see.
        scraper = ctx.scraper.open(raise_for_status=False)
        try:
            return await self._proxy(scraper, path, request)
        finally:
            # One scraper per proxied request, so it has to be closed: it owns a curl
            # session and, with a pool configured, a leased exit that the pool holds
            # until it is told otherwise.
            scraper.close()

    async def _proxy(self, scraper: Scraper, path: str, request: Request) -> Response:
        parsed = urlparse(path)
        apex_domain = parsed.hostname or ""
        target_origin = f"{parsed.scheme}://{parsed.netloc}"
        prefix_origin = urljoin(str(request.base_url), self.prefix)
        base_url = f"{prefix_origin}/{target_origin}"

        body = await request.body()

        headers = MutableHeaders(headers=dict(request.headers))
        if headers.get("host"):
            headers["host"] = apex_domain
        if headers.get("origin"):
            headers["origin"] = target_origin
        if headers.get("referer"):
            headers["referer"] = headers["referer"][len(prefix_origin) + 1 :]

        cookies = None
        domain_cookie = request.cookies.get(apex_domain)
        if domain_cookie:
            cookies = pickle.loads(base64.decodebytes(domain_cookie.encode()))

        try:
            resp = scraper.fetch(request.method, path, data=body or None)
        except Blocked as e:
            # The escalating path is out of options. Re-send once with the visitor's
            # own headers and cookies and no redirect following — their session may
            # carry a clearance this process has no way to earn.
            logger.warning(f"{path}: {e!r}")
            resp = scraper.transport.send(
                request.method,
                path,
                headers=dict(headers),
                data=body or None,
                cookies=cookies,
                allow_redirects=False,
            )

        if resp.status_code >= 400:
            return RedirectResponse(path)

        content_type = resp.headers.get("content-type", "")
        response = Response(
            media_type=content_type,
            status_code=resp.status_code,
            headers=dict((k, v) for k, v in resp.headers.items() if k.lower() not in _HOP_BY_HOP),
        )
        response.set_cookie(
            key=apex_domain,
            value=base64.encodebytes(pickle.dumps(resp.cookies)).decode(),
        )

        if resp.is_redirect:
            location = resp.headers.get("location", "")
            absolute = urljoin(path, location)
            response.headers["location"] = f"{prefix_origin}/{absolute}"
        elif "text/html" in content_type:
            html = resp.content.decode(errors="replace")
            html = helper.rewrite_html(html, target_origin)
            html = helper.replace_links(html, prefix_origin)
            if "<base href" not in html:
                html = html.replace("<head>", f'<head><base href="{base_url}/">')
            js = (
                browser_intercept_script()
                .replace("__BASE_ORIGIN__", target_origin)
                .replace("__BROWSE_PREFIX__", prefix_origin)
            )
            html = html.replace("<head>", f"<head><script>{js}</script>")
            response.body = html.encode()
        elif "text/css" in content_type:
            text = resp.content.decode(errors="replace")
            text = helper.rewrite_css(text, target_origin)
            text = helper.replace_links(text, prefix_origin)
            response.body = text.encode()
        elif "javascript" in content_type:
            text = resp.content.decode(errors="replace")
            text = helper.replace_links(text, prefix_origin)
            response.body = text.encode()
        else:
            response.body = resp.content

        if response.body:
            response.headers["content-length"] = f"{len(response.body)}"
        return response
