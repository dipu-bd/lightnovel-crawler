from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Path, Query, Security

from ...context import ctx
from ...dao import (
    ActivityType,
    Artifact,
    Chapter,
    LanguageCode,
    Novel,
    NovelSort,
    User,
    Volume,
)
from ...exceptions import ServerErrors
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
    language: Optional[LanguageCode] = Query(default=None, help="Language code"),
    tags: List[str] = Query(default=[], help="Match novels having all of these tags"),
    manga: Optional[bool] = Query(default=None, help="Filter manga/comic entries"),
    mtl: Optional[bool] = Query(default=None, help="Filter machine-translated entries"),
    min_chapters: int = Query(default=0, ge=0, help="Minimum chapter count"),
    sort: NovelSort = Query(default=NovelSort.updated, help="Sort order"),
) -> Paginated[Novel]:
    return ctx.novels.list(
        limit=limit,
        offset=offset,
        search=search.strip(),
        domain=domain.strip(),
        language=language.value if language else None,
        tags=[t.strip() for t in tags if t.strip()],
        manga=manga,
        mtl=mtl,
        min_chapters=min_chapters,
        sort=sort,
    )


@router.get(
    "/domains",
    summary="Returns a list of sources that are used in available novels",
)
def list_sources() -> Dict[str, int]:
    return ctx.novels.list_domains()


@router.get(
    "/tags",
    summary="Returns tags used across available novels with their counts",
)
def list_tags() -> Dict[str, int]:
    return ctx.novels.list_tags()


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
    volume: Optional[int] = Query(default=None),
) -> List[Artifact]:
    return ctx.artifacts.list_latest(novel_id, language, volume)


@router.get("/{novel_id}/glossaries", summary="Gets translation glossaries by language")
def get_novel_glossaries(
    novel_id: str = Path(),
    language: Optional[LanguageCode] = Query(default=None),
) -> Dict[str, Dict[str, str]]:
    return ctx.novels.list_glossaries(novel_id, language)


@router.put("/{novel_id}/glossary", summary="Replaces the translation glossary of a language")
def update_novel_glossary(
    novel_id: str = Path(),
    language: LanguageCode = Query(),
    terms: Dict[str, str] = Body(),
    user: User = Security(ensure_user),
) -> Dict[str, str]:
    # Glossary terms are injected into translations, so editing is gated the
    # same way as requesting a translation.
    if not ctx.tier.translation_enabled(user):
        raise ServerErrors.tier_not_allowed
    return ctx.novels.update_glossary(novel_id, language, terms)


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
