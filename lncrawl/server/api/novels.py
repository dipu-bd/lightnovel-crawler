from typing import Dict, List, Optional

from fastapi import APIRouter, Path, Query, Security

from ...context import ctx
from ...dao import ActivityType, Artifact, Chapter, LanguageCode, Novel, User, Volume
from ..models import Paginated
from ..security import ensure_admin, ensure_user

# The root router
router = APIRouter()


@router.get(
    "s",
    summary="Returns a list of novels",
)
def list_novels(
    search: str = Query(default="", help="Search query"),
    offset: int = Query(default=0, help="Offset"),
    limit: int = Query(default=20, le=100, help="Limit"),
    domain: str = Query(default="", help="Domain name"),
) -> Paginated[Novel]:
    return ctx.novels.list(
        limit=limit,
        offset=offset,
        search=search.strip(),
        domain=domain.strip(),
    )


@router.get(
    "/domains",
    summary="Returns a list of sources that are used in available novels",
)
def list_sources() -> Dict[str, int]:
    return ctx.novels.list_domains()


@router.get("/{novel_id}", summary="Returns a novel")
def get_novel(
    novel_id: str = Path(),
    language: Optional[LanguageCode] = Query(default=None),
    user: User = Security(ensure_user),
) -> Novel:
    ctx.activity.record(user.id, ActivityType.NOVEL, novel_id)
    if language:
        ctx.activity.record(user.id, ActivityType.NOVEL_TRANSLATION, novel_id)
    return ctx.novels.get(novel_id, language)


@router.get("/{novel_id}/languages", summary="Gets available translation languages")
def get_novel_languages(
    novel_id: str = Path(),
) -> List[LanguageCode]:
    return ctx.novels.list_translation_languages(novel_id)


@router.get("/{novel_id}/volumes", summary="Gets volumes")
async def get_novel_volumes(
    novel_id: str = Path(),
    language: Optional[LanguageCode] = Query(default=None),
) -> List[Volume]:
    return ctx.volumes.list(novel_id, language)


@router.get("/{novel_id}/chapters", summary="Gets all chapters")
async def get_novel_chapters(
    novel_id: str = Path(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    language: Optional[LanguageCode] = Query(default=None),
) -> Paginated[Chapter]:
    return ctx.chapters.list_page(
        limit=limit,
        offset=offset,
        novel_id=novel_id,
        language=language,
    )


@router.get("/{novel_id}/artifacts", summary="Gets latest artifacts")
async def get_novel_artifacts(
    novel_id: str = Path(),
    language: Optional[LanguageCode] = Query(default=None),
) -> List[Artifact]:
    return ctx.artifacts.list_latest(novel_id, language)


@router.get("/{novel_id}/recommended", summary="Gets recommended novels based on similarity")
def get_novel_recommended(
    novel_id: str = Path(),
    limit: int = Query(default=8, ge=4, le=20),
) -> List[Novel]:
    return ctx.recommendations.get(novel_id, limit)


@router.delete(
    "/{novel_id}",
    summary="Removes a novel",
    dependencies=[Security(ensure_admin)],
)
def delete_novel(
    novel_id: str = Path(),
) -> bool:
    ctx.novels.delete(novel_id)
    return True
