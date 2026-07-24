import asyncio
from contextlib import asynccontextmanager
import mimetypes
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from ..assets.version import get_version
from ..context import ctx
from ..exceptions import ServerErrors, get_exception_handlers
from .api import router as api
from .api.translator import TranslatorDashboard
from .middleware.staticfiles import CustomStaticFiles, StaticFilesGuard

web_dir = (Path(__file__).parent / "web").absolute()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        ctx.setup()
        ctx.mail.start()
        ctx.scheduler.start()
        ctx.recommendations.warmup()
        yield
    finally:
        ctx.destroy()


app = FastAPI(
    version=get_version(),
    title="Lightnovel Crawler",
    description="Download novels from online sources and generate e-books",
    lifespan=lifespan,
    exception_handlers=get_exception_handlers(),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    terms_of_service="https://raw.githubusercontent.com/lncrawl/lncrawl-web/refs/heads/artifacts/TERMS_OF_SERVICE.html",
    contact={
        "email": "lncrawl@pm.me",
        "name": "Lightnovel Crawler",
        "url": "https://github.com/lncrawl/lightnovel-crawler",
    },
    license_info={
        "name": "License: GPLv3",
        "url": "https://raw.githubusercontent.com/lncrawl/lightnovel-crawler/dev/LICENSE",
    },
)


# Add middleares
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Refresh-Token"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

app.add_middleware(StaticFilesGuard, prefix="/static")

# Experimental Features
if ctx.config.server.enable_browse_route:
    from .middleware.browser import BrowserNavigation

    app.add_middleware(BrowserNavigation, prefix="/browse")


# Add APIs
app.include_router(api, prefix="/api")

# Mount the embedded translator dashboard (admin-gated ASGI wrapper)
app.mount("/api/translator", TranslatorDashboard(), name="translator-dashboard")


# The dashboard's relative asset URLs only resolve under the prefix with a
# trailing slash; the SPA catch-all would otherwise swallow the bare path.
@app.get("/api/translator", include_in_schema=False)
async def translator_dashboard_root(request: Request) -> RedirectResponse:
    query = str(request.url.query)
    return RedirectResponse("/api/translator/" + (f"?{query}" if query else ""))


# Mount static files
app.mount("/static", CustomStaticFiles(), name="static")


# Lightweight liveness probe — no auth, used by Docker healthcheck
@app.get("/health", include_in_schema=False)
async def health():
    job_count = ctx.jobs.count()
    user_count = ctx.users.count()
    return {
        "status": "ok",
        "version": get_version(),
        "users": user_count,
        "jobs": job_count,
    }


# Mount frontend
@app.get("/{fallback:path}", include_in_schema=False)
async def serve_web(fallback: str):
    # Unknown API paths must fail fast, not silently serve the SPA shell.
    if fallback == "api" or fallback.startswith("api/"):
        raise ServerErrors.not_found
    target_file = web_dir.joinpath(fallback)
    if not target_file.is_relative_to(web_dir):
        raise ServerErrors.not_found
    loop = asyncio.get_event_loop()
    if not await loop.run_in_executor(None, target_file.is_file):
        target_file = web_dir / "index.html"
    mime_type, _ = mimetypes.guess_type(target_file)
    if not mime_type:
        mime_type = "application/octet-stream"
    if mime_type == "text/javascript":
        mime_type = "application/javascript"
    if target_file.name in {"index.html", "sw.js", "registerSW.js"}:
        return FileResponse(
            target_file,
            media_type=mime_type,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
    return FileResponse(target_file, media_type=mime_type)
