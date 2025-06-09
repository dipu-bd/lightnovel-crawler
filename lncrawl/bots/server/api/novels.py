from typing import List

from fastapi import APIRouter, Depends, Path, Query, Security
from fastapi.responses import StreamingResponse

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.novel import Artifact, Novel
from ..models.pagination import Paginated
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("s", summary='Returns a list of novels',
            dependencies=[Security(ensure_user)],)
def list_novels(
    ctx: ServerContext = Depends(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    with_orphans: bool = Query(default=False),
) -> Paginated[Novel]:
    return ctx.novels.list(
        limit=limit,
        offset=offset,
        with_orphans=with_orphans,
    )


@router.get("/{novel_id}", summary='Returns a novel')
def get_novel(
    novel_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> Novel:
    return ctx.novels.get(novel_id)


@router.get("/{novel_id}/artifacts", summary='Returns cached artifacts',
            dependencies=[Security(ensure_user)])
def get_novel_artifacts(
    novel_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> List[Artifact]:
    return ctx.novels.get_artifacts(novel_id)


@router.get("/{novel_id}/cover", summary='Returns a novel cover')
async def get_novel_cover(
    novel_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> StreamingResponse:
    novel = ctx.novels.get(novel_id)
    if not novel.cover:
        raise AppErrors.no_novel_cover
    return await ctx.fetch.image(novel.cover)
