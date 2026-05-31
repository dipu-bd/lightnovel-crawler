from typing import Optional

from fastapi import APIRouter, Path, Query, Security

from ...context import ctx
from ...dao import ActivityType, Chapter, Job, LanguageCode, User, Volume
from ..models import Paginated
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("/{volume_id}", summary="Returns a volume details")
def get_volume(
    volume_id: str = Path(),
    user: User = Security(ensure_user),
) -> Volume:
    ctx.activity.record(user.id, ActivityType.VOLUME, volume_id)
    return ctx.volumes.get(volume_id)


@router.get("/{volume_id}/fetch", summary="Create a job to fetch volume")
def fetch_volume(
    user: User = Security(ensure_user),
    volume_id: str = Path(),
) -> Job:
    return ctx.jobs.fetch_volume(user, volume_id)


@router.get("/{volume_id}/chapters", summary="Gets all chapters")
async def get_volume_chapters(
    volume_id: str = Path(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    language: Optional[LanguageCode] = Query(default=None),
) -> Paginated[Chapter]:
    return ctx.chapters.list_page(
        limit=limit,
        offset=offset,
        volume_id=volume_id,
        language=language,
    )
