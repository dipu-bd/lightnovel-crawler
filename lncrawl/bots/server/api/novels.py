from fastapi import APIRouter, Depends, Path, Query

from ..context import ServerContext

# The root router
router = APIRouter()


@router.get("s", summary='Returns a list of novels')
def list_novels(
    ctx: ServerContext = Depends(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    with_orphans: bool = Query(default=False),
):
    return ctx.novels.list(
        limit=limit,
        offset=offset,
        with_orphans=with_orphans,
    )


@router.get("/{novel_id}", summary='Returns a novel')
def get_novel(
    novel_id: str = Path(),
    ctx: ServerContext = Depends(),
):
    return ctx.novels.get(novel_id)


@router.get("/{novel_id}/artifacts", summary='Returns cached artifacts')
def get_novel_artifacts(
    novel_id: str = Path(),
    ctx: ServerContext = Depends(),
):
    return ctx.novels.get_artifacts(novel_id)
