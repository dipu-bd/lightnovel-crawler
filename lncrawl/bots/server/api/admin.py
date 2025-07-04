from fastapi import APIRouter, Depends

from ..context import ServerContext
from lncrawl.core.sources import update_sources

# The root router
router = APIRouter()


@router.post("/update-sources", summary='Update sources from the repository')
def update(ctx: ServerContext = Depends()) -> int:
    return update_sources()
