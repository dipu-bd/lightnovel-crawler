from pathlib import Path
from urllib.parse import quote, unquote

from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from ...context import ctx
from ...dao import ActivityType
from ...exceptions import ServerErrors

_WHITELIST = frozenset(["novels", "images"])


class StaticFilesGuard(BaseHTTPMiddleware):
    def __init__(self, app, prefix: str = "/static") -> None:
        self.prefix = prefix
        super().__init__(app)

    @property
    def prefix_len(self):
        return len(self.prefix) + 1

    async def dispatch(self, request, call_next) -> Response:
        path = unquote(request.url.path)
        if not path.startswith(self.prefix):
            return await call_next(request)

        file_path = path[self.prefix_len :]
        first_part = file_path.split("/")[0]
        if first_part not in _WHITELIST or not ctx.files.exists(file_path):
            return ServerErrors.no_such_file.to_response()

        # Propagate decoded path so StaticFiles finds the file (handles Unicode filenames)
        request.scope["path"] = path

        token = request.query_params.get("token")
        if not token:
            return ServerErrors.forbidden.to_response()

        user = ctx.users.verify_token(token, [])
        if not user.is_active:
            return ServerErrors.inactive_user.to_response()

        request.scope["user"] = user
        return await call_next(request)


class CustomStaticFiles(StaticFiles):
    def __init__(self) -> None:
        super().__init__(directory=ctx.config.app.app_dir)

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)

        if resp.status_code < 400:
            if "/artifacts/" in path:
                filename = Path(path).name

                # RFC 5987: ASCII fallback + UTF-8 for non-ASCII filenames
                ascii_fallback = filename.encode("ascii", "replace").decode("ascii")
                utf8_encoded = quote(filename, safe="", encoding="utf-8")
                resp.headers["content-disposition"] = (
                    f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{utf8_encoded}"
                )

                if path.endswith(".epub"):
                    resp.media_type = "application/epub+zip"
                    resp.headers["content-type"] = "application/epub+zip"

        user = scope["user"]
        ctx.activity.record(user.id, ActivityType.DOWNLOAD, path)

        return resp
