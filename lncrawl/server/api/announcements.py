from typing import List, Literal

from fastapi import APIRouter, Body, Path, Query, Security

from ...context import ctx
from ...dao import Announcement, User
from ..models import AnnouncementCreateRequest, AnnouncementUpdateRequest
from ..security import ensure_admin

router = APIRouter()


@router.get("/active", summary="Get active announcements")
def list_active() -> List[Announcement]:
    return ctx.announcements.list_active()


@router.get(
    "",
    summary="List all announcements (admin)",
    dependencies=[Security(ensure_admin)],
)
def list_all(
    offset: int = Query(default=0),
    limit: int = Query(default=50, le=100),
) -> List[Announcement]:
    return ctx.announcements.list_all(offset=offset, limit=limit)


@router.post("", summary="Create announcement")
def create_announcement(
    user: User = Security(ensure_admin),
    body: AnnouncementCreateRequest = Body(...),
) -> Announcement:
    return ctx.announcements.create(
        user=user,
        title=body.title,
        message=body.message,
        type=body.type,
        is_active=body.is_active,
    )


@router.patch(
    "/{announcement_id}",
    summary="Update announcement",
    dependencies=[Security(ensure_admin)],
)
def update_announcement(
    announcement_id: str = Path(),
    body: AnnouncementUpdateRequest = Body(...),
) -> Announcement:
    return ctx.announcements.update(
        announcement_id=announcement_id,
        title=body.title,
        message=body.message,
        type=body.type,
        is_active=body.is_active,
        bump_version=body.bump_version,
    )


@router.post(
    "/{announcement_id}/interact",
    summary="Track announcement interaction (click or close)",
)
def track_interaction(
    announcement_id: str = Path(),
    interaction_type: Literal["click", "close"] = Body(..., embed=True),
) -> bool:
    return ctx.announcements.track_interaction(announcement_id, interaction_type)


@router.delete(
    "/{announcement_id}",
    summary="Delete announcement",
    dependencies=[Security(ensure_admin)],
)
def delete_announcement(
    announcement_id: str = Path(),
) -> bool:
    return ctx.announcements.delete(announcement_id)
