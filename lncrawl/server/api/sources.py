from typing import List

from fastapi import APIRouter, Body, Path, Query, Security
from fastapi.responses import JSONResponse, StreamingResponse

from ...context import ctx
from ...dao import ActivityType, User
from ...exceptions import ServerErrors
from ..models import (
    CrawlerTestRequest,
    PRCreateRequest,
    PRResponse,
    SourceItem,
)
from ..security import ensure_user

router = APIRouter()


@router.get(
    "s",
    summary="Returns a list of supported sources",
    response_model=List[SourceItem],
)
def list_sources(
    skip_rejected: bool = Query(default=False, help="Send true to skip rejected sources"),
    user: User = Security(ensure_user),
):
    ctx.activity.record(user.id, ActivityType.SOURCES, "sources")
    count = ctx.novels.list_domains()
    result = ctx.sources.list(
        include_rejected=not skip_rejected,
    )
    for item in result:
        item.total_novels = count.get(item.domain, 0)
    return JSONResponse(
        content=[item.model_dump() for item in result],
        headers={
            "ETag": str(ctx.sources.version),
            "Cache-Control": "public, max-age=14400",
        },
    )


@router.get(
    "/{domain}",
    summary="Get source item",
)
def get_source(domain: str) -> SourceItem:
    source = ctx.sources.get_source(domain)
    if source is None:
        raise ServerErrors.no_crawler.with_extra(domain)
    return source


@router.get(
    "/{domain}/code",
    summary="Get source crawler file content",
)
def get_source_code(domain: str) -> str:
    ctx.sources.update()
    return ctx.github.get_source_code(domain)


@router.get(
    "/{domain}/pr",
    summary="Create a GitHub PR with an edited source crawler",
)
def get_source_pr(domain: str = Path()) -> PRResponse:
    return ctx.github.fetch_source_pr(domain)


@router.post(
    "/{domain}/pr",
    summary="Create a GitHub PR with an edited source crawler",
)
def create_source_pr(
    domain: str = Path(),
    req: PRCreateRequest = Body(...),
    user: User = Security(ensure_user),
) -> PRResponse:
    return ctx.github.create_source_pr(user, domain, req)


@router.post(
    "/{domain}/test",
    summary="Test crawler source code against a novel URL (Admin only)",
)
async def test_source(
    domain: str = Path(),
    req: CrawlerTestRequest = Body(...),
    user: User = Security(ensure_user),
) -> StreamingResponse:
    # ctx.sources.update()
    code = ctx.github.get_source_code(domain)
    if code != req.content and not user.is_admin:
        return StreamingResponse(
            "<!> Modified source code can only be executed by administrators."
            " Revert your changes or contact an admin to proceed.",
            media_type="text/plain",
        )
    return StreamingResponse(
        ctx.sources.test_source(req.url, req.content),
        media_type="text/event-stream",
    )
