from fastapi import APIRouter, Depends, Security

from ..security import ensure_admin, ensure_user
from .admin import router as admin
from .artifacts import router as artifact
from .auth import router as auth
from .jobs import router as job
from .novels import router as novel
from .runner import router as runner
from .users import router as user
from .meta import router as meta

router = APIRouter()

router.include_router(
    auth,
    prefix='/auth',
    tags=['Auth'],
)

router.include_router(
    job,
    prefix='/job',
    tags=['Jobs'],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    novel,
    prefix='/novel',
    tags=['Novels'],
)

router.include_router(
    artifact,
    prefix='/artifact',
    tags=['Artifacts'],
)

router.include_router(
    meta,
    prefix='/meta',
    tags=['Metadata'],
)

router.include_router(
    user,
    prefix='/user',
    tags=['Users'],
    dependencies=[Depends(ensure_admin)],
)

router.include_router(
    runner,
    prefix='/runner',
    tags=['Runner'],
    dependencies=[Depends(ensure_admin)],
)

router.include_router(
    admin,
    prefix='/admin',
    tags=['Admin'],
    dependencies=[Depends(ensure_admin)],
)
