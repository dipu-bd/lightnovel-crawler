import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from ...assets.version import get_version
from .context import ServerContext

app = FastAPI(
    version=get_version(),
    title="Lightnovel Crawler",
    description="Download novels from online sources and generate e-books",
    on_shutdown=[ServerContext().cleanup],
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
