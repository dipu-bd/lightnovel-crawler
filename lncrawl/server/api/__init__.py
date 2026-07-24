from fastapi import APIRouter, Security

from ..security import ensure_admin, ensure_user
from .admin import router as admin
from .announcements import router as announcement
from .artifacts import router as artifact
from .auth import router as auth
from .chapters import router as chapter
from .feedback import router as feedback
from .history import router as history
from .jobs import router as job
from .libraries import router as library
from .lsp import router as lsp
from .meta import router as metadata
from .novels import router as novel
from .settings import router as settings
from .sources import router as sources
from .users import router as user
from .volumes import router as volume

router = APIRouter()

# WebSocket routers handle their own auth and are mounted first so they don't
# inherit HTTP security dependencies from the parent router.
router.include_router(lsp, tags=["LSP"])

router.include_router(
    auth,
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(
    user,
    prefix="/user",
    tags=["Users"],
    dependencies=[Security(ensure_admin)],
)

router.include_router(
    settings,
    prefix="/settings",
    tags=["Settings"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    job,
    prefix="/job",
    tags=["Jobs"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    novel,
    prefix="/novel",
    tags=["Novels"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    library,
    prefix="/library",
    tags=["Libraries"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    volume,
    prefix="/volume",
    tags=["Volumes"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    chapter,
    prefix="/chapter",
    tags=["Chapters"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    artifact,
    prefix="/artifact",
    tags=["Artifacts"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    history,
    prefix="/read-history",
    tags=["Read History"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    feedback,
    prefix="/feedback",
    tags=["Feedback"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    metadata,
    prefix="/meta",
    tags=["Metadata"],
)

router.include_router(
    announcement,
    prefix="/announcement",
    tags=["Announcements"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    sources,
    prefix="/source",
    tags=["Sources"],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    admin,
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Security(ensure_admin)],
)


@router.api_route("/ping", methods=["GET", "HEAD", "OPTIONS"], include_in_schema=False)
def ping() -> str:
    return "pong"
