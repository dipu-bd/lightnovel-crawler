from contextlib import asynccontextmanager
import mimetypes
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse

from ..assets.version import get_version
from ..context import ctx
from ..exceptions import ServerErrors, get_exception_handlers
from .api import router as api
from .middleware.staticfiles import CustomStaticFiles, StaticFilesGuard

web_dir = (Path(__file__).parent / "web").absolute()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        ctx.setup()
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
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

app.add_middleware(StaticFilesGuard, prefix="/static")

# Add APIs
app.include_router(api, prefix="/api")

# Mount static files
app.mount("/static", CustomStaticFiles(), name="static")


# Mount frontend
@app.get("/{fallback:path}", include_in_schema=False)
async def serve_web(fallback: str):
    target_file = web_dir.joinpath(fallback)
    if not target_file.is_relative_to(web_dir):
        raise ServerErrors.not_found
    if not target_file.is_file():
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
