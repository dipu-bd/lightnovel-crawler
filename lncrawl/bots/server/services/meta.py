from functools import lru_cache
from typing import Dict
from urllib.parse import urlparse

from fastapi import APIRouter

from lncrawl.core.sources import crawler_list, rejected_sources

from ..context import ServerContext
from ..models.meta import SupportedSource

# The root router
router = APIRouter()


class MetadataService:
    def __init__(self, ctx: ServerContext) -> None:
        self.ctx = ctx

    @lru_cache()
    def list_supported_sources(self):
        # load_sources()
        supported: Dict[str, SupportedSource] = {}
        for crawler in crawler_list.values():
            for url in crawler.base_url:
                no_www = url.replace("://www.", "://")
                domain = urlparse(no_www).hostname
                if not domain:
                    continue
                supported[domain] = SupportedSource(
                    url=url,
                    domain=domain,
                    has_manga=crawler.has_manga,
                    has_mtl=crawler.has_mtl,
                    is_disabled=(url in rejected_sources),
                    disable_reason=rejected_sources.get(domain) or '',
                    language=crawler.language,
                    can_login=getattr(crawler, 'can_login', False),
                    can_logout=getattr(crawler, 'can_logout', False),
                    can_search=getattr(crawler, 'can_search', False),
                )
        return list(sorted(supported.values(), key=lambda x: x.domain))
