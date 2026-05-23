from typing import List, Optional

from fastapi import APIRouter, Path, Query, Security

from ...context import ctx
from ...dao import Chapter, ChapterImage, Job, User
from ..models import ReadChapterResponse
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("/{chapter_id}", summary="Returns a chapter details")
def get_chapter(
    chapter_id: str = Path(),
) -> Chapter:
    return ctx.chapters.get(chapter_id)


@router.get("/{chapter_id}/images", summary="Gets list of chapter images")
async def get_chapter_images(
    chapter_id: str = Path(),
    available_only: bool = Query(default=False, description="List only available images"),
) -> List[ChapterImage]:
    return ctx.images.list(
        chapter_id=chapter_id,
        is_crawled=available_only,
    )


@router.get("/{chapter_id}/read", summary="Get chapter content for reading")
def read_chapter(
    chapter_id: str = Path(),
    user: User = Security(ensure_user),
    language: Optional[str] = Query(
        default=None,
        description="Target language code, e.g. 'fr', 'zh-CN'",
    ),
    auto_fetch: Optional[bool] = Query(
        default=None,
        description="Fetch content automatically if not available",
    ),
) -> ReadChapterResponse:
    return ctx.chapters.read(
        user,
        chapter_id,
        language=language,
        auto_fetch=auto_fetch,
    )


@router.get("/{chapter_id}/fetch", summary="Create a job to fetch chapter content")
def fetch_chapter(
    user: User = Security(ensure_user),
    chapter_id: str = Path(),
) -> Job:
    job = ctx.jobs.get_chapter_job(user.id, chapter_id)
    if not job:
        job = ctx.jobs.fetch_chapter(user, chapter_id)
    return job


@router.get("/{chapter_id}/translate", summary="Create a job to translate chapter content")
def translate_chapter(
    user: User = Security(ensure_user),
    chapter_id: str = Path(),
    language: str = Query(description="Target language code, e.g. 'fr', 'zh-CN'"),
) -> Job:
    job = ctx.jobs.get_translation_job(user.id, chapter_id, language)
    if not job:
        job = ctx.jobs.translate_chapter(user, chapter_id, language)
    return job
