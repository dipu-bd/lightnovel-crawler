import asyncio
import logging
from pathlib import Path
import threading
from threading import Event, Thread
import traceback
from typing import Dict, List, Optional, Type

from ...context import ctx
from ...core import Crawler
from ...exceptions import ServerErrors
from ...server.models import CrawlerIndex, CrawlerInfo, SourceItem
from ...utils.event_lock import EventLock
from ...utils.fts_store import FTSStore
from ...utils.text_tools import normalize
from ...utils.url_tools import extract_host, normalize_url
from .helper import (
    batch_import,
    create_crawler_info,
    create_source_item,
    load_offline_source,
    save_source,
)
from .tester import run_crawler_test

logger = logging.getLogger(__name__)


class Sources:
    def __init__(self) -> None:
        self._signal: Event
        self._store: FTSStore
        self._index: CrawlerIndex
        self._sync_thread: Thread
        self._sync_lock = EventLock()
        self.rejected: Dict[str, str] = {}  # Map of host -> rejection reason
        self.crawlers: Dict[str, Type[Crawler]] = {}  # Map of cid -> crawler
        self.info: Dict[str, CrawlerInfo] = {}  # Map of cid -> crawler info
        self.sources: Dict[str, SourceItem] = {}  # Map of host -> source item
        self._cache: Dict[str, Crawler] = {}  # Map of cid -> crawler instance

    @property
    def version(self) -> int:
        if not hasattr(self, "_index"):
            raise ServerErrors.source_not_loaded
        return self._index.v

    def is_rejected(self, url: str) -> Optional[str]:
        host = extract_host(url)
        return self.rejected.get(host)

    def close(self):
        self._sync_lock.abort()
        if hasattr(self, "_signal"):
            self._signal.set()
        if hasattr(self, "_store"):
            self._store.close()
        if hasattr(self, "_index"):
            del self._index
        self.rejected.clear()
        self.sources.clear()

    def ensure_load(self):
        if hasattr(self, "_sync_thread") and self._sync_thread:
            self._sync_thread.join()
            del self._sync_thread

    def load(self, sync_remote=True):
        with self._sync_lock:
            self._signal = Event()
            self._store = FTSStore()

            # load offline sources first
            self.load_index(load_offline_source(sync_remote))

            # check online sources update
            if sync_remote:
                t = Thread(target=self.update)
                t.start()
                self._sync_thread = t

    def update(self) -> None:
        with self._sync_lock:
            logger.info(f"Sync online sources (current={self.version})")
            online_index = ctx.github.fetch_online_source()
            if not hasattr(self, "_index"):
                return
            if online_index.v <= self._index.v:
                logger.info("Sources are up to date")
                return

            # save the latest index
            user_file = ctx.config.crawler.user_index_file
            save_source(user_file, online_index)

            # download latest source files
            for id, source in online_index.crawlers.items():
                current = self._index.crawlers.get(id)
                if current and current.version >= source.version:
                    continue
                try:
                    ctx.github.download_online_source(source.file_path)
                    logger.debug(f"Downloaded source: {source.file_path}")
                except Exception:
                    logger.warning(f"Failed to download source: {source.file_path}", exc_info=True)

            # load the online index
            self.load_index(online_index)
            logger.info("Source synced.")

    def load_index(self, index: CrawlerIndex) -> None:
        self._index = index

        # update rejected list
        self.rejected.clear()
        for url, reason in index.rejected.items():
            host = extract_host(url)
            self.rejected[host] = reason

        # dynamically import all crawlers
        self.info.clear()
        self.crawlers.clear()
        self.sources.clear()
        self._cache.clear()
        self.load_crawlers(
            *ctx.config.crawler.local_sources.glob("**/*.py"),
            *ctx.config.crawler.user_sources.glob("**/*.py"),
        )

    def load_crawlers(self, *files: Path):
        for crawler in batch_import(*files):
            self.add_crawler(crawler)

    def add_crawler(self, crawler: Type[Crawler]):
        # add to index if not available
        name = crawler.__name__
        cid = getattr(crawler, "__id__")  # crawler id
        if cid in self._index.crawlers:
            info = self._index.crawlers[cid]
        else:
            logger.info(f"Found non-indexed crawler: {name}")
            info = create_crawler_info(crawler)
            self._index.crawlers[cid] = info

        # skip this crawler if it is not the latest
        if cid in self.info and info.version < self.info[cid].version:
            return
        self.info[cid] = info
        self.crawlers[cid] = crawler

        # load source items
        for url in info.base_urls:
            self.add_source(url, info)

    def add_source(self, url: str, info: CrawlerInfo):
        item = create_source_item(url, info, self.rejected)
        # skip this item if it is not the latest
        if item.domain in self.sources and item.version < self.sources[item.domain].version:
            return
        self.sources[item.domain] = item

        # add keys for searching
        self._store.insert(normalize_url(url), item.domain)

    def list(
        self,
        query: Optional[str] = None,
        *,
        include_rejected: bool = False,
        can_search: Optional[bool] = None,
        can_login: Optional[bool] = None,
        has_mtl: Optional[bool] = None,
        has_manga: Optional[bool] = None,
    ) -> List[SourceItem]:
        self.ensure_load()
        domains = self._store.search(normalize(query)) if query else None
        if domains is not None and len(domains) == 0:
            return []
        return [
            item
            for item in self.sources.values()
            if all(
                [
                    domains is None or item.domain in domains,
                    has_mtl is None or item.has_mtl == has_mtl,
                    has_manga is None or item.has_manga == has_manga,
                    can_login is None or item.can_login == can_login,
                    can_search is None or item.can_search == can_search,
                    include_rejected or item.is_disabled,
                ]
            )
        ]

    def get_domain(self, url: str) -> str:
        host = extract_host(url)
        if not host:
            raise ServerErrors.invalid_url
        if host in self.rejected:
            raise ServerErrors.host_rejected.with_extra(self.rejected[host])
        return host

    def get_source(self, domain: str) -> SourceItem:
        self.ensure_load()
        if domain.startswith("www."):
            domain = domain[4:]
        source = self.sources.get(domain)
        if not source:
            raise ServerErrors.no_crawler.with_extra(source)
        return source

    def get_info(self, domain: str) -> CrawlerInfo:
        source = self.get_source(domain)
        return self.info[source.crawler_id]

    def get_crawler(self, domain: str) -> Type[Crawler]:
        source = self.get_source(domain)
        return self.crawlers[source.crawler_id]

    def find_crawler(self, url: str) -> Type[Crawler]:
        self.ensure_load()
        return self.get_crawler(self.get_domain(url))

    def init_crawler(
        self,
        url: str,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
        renew: bool = False,
    ) -> Crawler:
        domain = self.get_domain(url)
        source = self.get_source(domain)
        cid = source.crawler_id
        constructor = self.crawlers[cid]
        if constructor in self._cache:
            if renew:
                self._cache.pop(cid).close()
            else:
                return self._cache[cid]

        # create instance
        ctx.logger.debug(f"Creating crawler instance for {url}")
        crawler = constructor(
            origin=source.url,
            workers=workers,
            parser=parser,
        )
        crawler.initialize()

        self._cache[cid] = crawler
        return crawler

    async def test_source(self, url: str, content: str):
        # WARNING: This function executes arbitrary Python source code directly in the
        # running process. It is intended solely for trusted developer use. Never pass
        # unverified or user-supplied content — doing so is a critical security risk
        # (remote code execution). USE WITH EXTREME CAUTION.
        event = Event()
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()

        def emit(item: str = "") -> None:
            loop.call_soon_threadsafe(queue.put_nowait, item + "\n")

        def run():
            try:
                run_crawler_test(url, content, emit)
                emit("\nTEST PASSED!")
            except Exception as e:
                emit(f"<!> {repr(e)}\n{traceback.format_exc()}")
                emit("\nTEST FAILED!")
            finally:
                event.set()
                emit("END")

        threading.Thread(target=run, daemon=True).start()

        while True:
            item = await queue.get()
            if event.is_set() and item == "END\n":
                break
            yield item
