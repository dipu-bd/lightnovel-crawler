import asyncio
from pathlib import Path
from urllib.parse import quote, unquote

from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from ...context import ctx
from ...dao import ActivityType
from ...exceptions import ServerErrors

_WHITELIST = frozenset(["novels", "images", "sources"])


class StaticFilesGuard:
    def __init__(self, app, prefix: str = "/static") -> None:
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = unquote(scope["path"])
        if not path.startswith(self.prefix):
            await self.app(scope, receive, send)
            return

        file_path = path[len(self.prefix) + 1 :]
        first_part = file_path.split("/")[0]
        if first_part not in _WHITELIST or not ctx.files.exists(file_path):
            await ServerErrors.no_such_file.to_response()(scope, receive, send)
            return

        # Propagate decoded path so StaticFiles finds the file (handles Unicode filenames)
        scope["path"] = path

        token = Request(scope, receive).query_params.get("token")
        if not token:
            await ServerErrors.forbidden.to_response()(scope, receive, send)
            return

        loop = asyncio.get_event_loop()
        user = await loop.run_in_executor(None, lambda: ctx.users.verify_token(token, []))
        if not user.is_active:
            await ServerErrors.inactive_user.to_response()(scope, receive, send)
            return

        scope["user"] = user
        await self.app(scope, receive, send)


class CustomStaticFiles(StaticFiles):
    def __init__(self) -> None:
        super().__init__(directory=ctx.config.app.app_dir)

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        user = scope["user"]

        if resp.status_code >= 400:
            return resp

        if "/artifacts/" in path:
            filename = Path(path).name
            ctx.activity.record(user.id, ActivityType.ARTIFACT, path)

            # RFC 5987: ASCII fallback + UTF-8 for non-ASCII filenames
            ascii_fallback = filename.encode("ascii", "replace").decode("ascii")
            utf8_encoded = quote(filename, safe="", encoding="utf-8")
            resp.headers["content-disposition"] = (
                f"inline; filename=\"{ascii_fallback}\"; filename*=UTF-8''{utf8_encoded}"
            )

            if path.endswith(".epub"):
                resp.media_type = "application/epub+zip"
                resp.headers["content-type"] = "application/epub+zip"

        return resp
