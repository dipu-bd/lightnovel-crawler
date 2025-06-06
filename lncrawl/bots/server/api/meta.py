from typing import Iterable

from fastapi import APIRouter

from lncrawl.core.sources import crawler_list

from ..models.meta import SupportedSource

# The root router
router = APIRouter()


@router.get("/supported-sources", summary='Returns a list of supported sources')
def list_supported_sources() -> Iterable[SupportedSource]:
    supported = set()
    for crawler in crawler_list.values():
        for url in crawler.base_url:
            if url in supported:
                continue
            supported.add(url)
            yield SupportedSource(
                url=url,
                has_manga=crawler.has_manga,
                has_mtl=crawler.has_mtl,
                is_disabled=crawler.is_disabled,
                disable_reason=crawler.disable_reason,
                language=crawler.language,
                can_login=getattr(crawler, 'can_login', False),
                can_logout=getattr(crawler, 'can_logout', False),
                can_search=getattr(crawler, 'can_search', False),
            )
