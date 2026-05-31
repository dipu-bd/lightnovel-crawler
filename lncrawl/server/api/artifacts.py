from typing import List, Optional

from fastapi import APIRouter, Path, Query, Security

from ...context import ctx
from ...dao import Artifact, LanguageCode, OutputFormat, User
from ..models import Paginated
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get(
    "s",
    summary="Returns a list of artifacts",
    dependencies=[Security(ensure_user)],
)
def list_artifacts(
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    job_id: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    novel_id: Optional[str] = Query(default=None),
    format: Optional[OutputFormat] = Query(default=None),
    language: Optional[LanguageCode] = Query(default=None),
) -> Paginated[Artifact]:
    return ctx.artifacts.list(
        limit=limit,
        offset=offset,
        user_id=user_id,
        job_id=job_id,
        format=format,
        novel_id=novel_id,
        language=language,
    )


@router.get("/enabled-formats", summary="Returns a list of enabled formats for the current user")
def get_enabled_formats(
    user: User = Security(ensure_user),
) -> List[OutputFormat]:
    return list(sorted(ctx.tier.enabled_formats(user)))


@router.get(
    "/{artifact_id}",
    summary="Returns a artifact",
    dependencies=[Security(ensure_user)],
)
def get_artifact(
    artifact_id: str = Path(),
) -> Artifact:
    return ctx.artifacts.get(artifact_id)
