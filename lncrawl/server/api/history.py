from typing import Dict

from fastapi import APIRouter, Path, Query, Security

from ...context import ctx
from ...dao import User
from ..models import ContinueReadingResponse, Paginated, ReadHistoryNovel
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("", summary="List recently read novels for the current user")
def list_read_history(
    user: User = Security(ensure_user),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
) -> Paginated[ReadHistoryNovel]:
    return ctx.history.list_recent_novels(user.id, offset, limit)


@router.get("/continue", summary="Resolve the chapter to continue reading from")
def continue_reading(
    user: User = Security(ensure_user),
    novel_id: str = Query(description="Novel id"),
) -> ContinueReadingResponse:
    return ctx.history.continue_reading(user.id, novel_id)


@router.post("/add/{chapter_id}", summary="Mark a chapter as read")
def mark_as_read(
    user: User = Security(ensure_user),
    chapter_id: str = Path(),
) -> bool:
    ctx.history.add(user.id, chapter_id)
    return True


@router.get("/by-novel", summary="Return history by novel id")
def get_read_history_by_novels(
    user: User = Security(ensure_user),
    novel_id: str = Query(description="Novel id (can be comma separated)"),
) -> Dict[str, bool]:
    return ctx.history.list(user.id, novel_id=novel_id)


@router.get("/by-volume", summary="Return history by volume id")
def get_read_history_by_volumes(
    user: User = Security(ensure_user),
    volume_id: str = Query(description="Volume id (can be comma separated)"),
) -> Dict[str, bool]:
    return ctx.history.list(user.id, volume_id=volume_id)


@router.get("/by-chapter", summary="Return history by chapter id")
def get_read_history_by_chapters(
    user: User = Security(ensure_user),
    chapter_id: str = Query(description="Chapter id (can be comma separated)"),
) -> Dict[str, bool]:
    return ctx.history.list(user.id, chapter_id=chapter_id)
