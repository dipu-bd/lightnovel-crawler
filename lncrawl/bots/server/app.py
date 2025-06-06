import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse

from lncrawl.assets.version import get_version

from .context import ServerContext

app = FastAPI(
    version=get_version(),
    title="Lightnovel Crawler",
    description="Download novels from online sources and generate e-books",
    on_shutdown=[ServerContext().cleanup],
    on_startup=[ServerContext().prepare],
)

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


try:
    from .api import router as api
    app.include_router(api, prefix='/api')
except ImportError:
    traceback.print_exc()


web_dir = (Path(__file__).parent / 'web').absolute()
if web_dir.is_dir():
    @app.get("/{fallback:path}", include_in_schema=False)
    async def serve_static(fallback: str):
        target_file = web_dir.joinpath(fallback)
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(web_dir / "index.html")
