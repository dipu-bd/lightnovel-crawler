import logging
from pathlib import Path
from threading import Event
from typing import Dict, List, Optional, Type

from ...context import ctx
from ...core.crawler import Crawler
from ...core.taskman import TaskManager
from ...exceptions import ServerErrors
from ...server.models import CrawlerIndex, CrawlerInfo, SourceItem
from ...utils.fts_store import FTSStore
from ...utils.text_tools import normalize
from ...utils.url_tools import extract_host, normalize_url
from . import utils

logger = logging.getLogger(__name__)


class Sources:
    def __init__(self) -> None:
        self._signal: Event
        self._store: FTSStore
        self._index: CrawlerIndex
        self._taskman: TaskManager
        self.rejected: Dict[str, str] = {}  # Map of host -> rejection reason
        self.crawlers: Dict[str, Type[Crawler]] = {}  # Map of host/id -> crawler

    @property
    def version(self) -> int:
        if not self._index:
            raise ServerErrors.source_not_loaded
        return self._index.v

    def is_rejected(self, url: str) -> Optional[str]:
        host = extract_host(url)
        return self.rejected.get(host)

    def close(self):
        if hasattr(self, "_signal"):
            self._signal.set()
        if hasattr(self, "_store"):
            self._store.close()
        if hasattr(self, "_taskman"):
            self._taskman.close()
        if hasattr(self, "_index"):
            del self._index
        self.rejected.clear()
        self.crawlers.clear()

    def load(self, sync_remote=True):
        self._signal = Event()
        self._store = FTSStore()
        self._taskman = TaskManager(10)

        # load offline sources first
        self.load_index(utils.load_offline_source(sync_remote))

        # dynamically import all crawlers
        self._taskman.submit_task(
            self.load_crawlers,
            *ctx.config.crawler.local_sources.glob("**/*.py"),
            *ctx.config.crawler.user_sources.glob("**/*.py"),
        )

        # run background task get online update
        if sync_remote:
            self._taskman.submit_task(self.update)

    def ensure_load(self):
        self._taskman.as_completed(
            disable_bar=True,
            signal=self._signal,
        )

    def load_index(self, index: CrawlerIndex) -> None:
        self._index = index

        # update rejected list
        self.rejected.clear()
        for url, reason in index.rejected.items():
            host = extract_host(url)
            self.rejected[host] = reason

    def load_crawlers(self, *files: Path) -> List[CrawlerInfo]:
        futures = [self._taskman.submit_task(utils.import_crawlers, file) for file in files]
        return [
            self.add_crawler(crawler)
            for crawlers in self._taskman.resolve_as_generator(
                futures,
                disable_bar=True,
                signal=self._signal,
            )
            if crawlers
            for crawler in crawlers
            if issubclass(crawler, Crawler)
        ]

    def add_crawler(self, crawler: Type[Crawler]) -> CrawlerInfo:
        sid = getattr(crawler, "__id__")  # crawler id
        file = getattr(crawler, "__file__")  # file path
        urls = getattr(crawler, "base_url")  # always a list
        version = getattr(crawler, "version")  # last edit time

        # add to index if not available
        if sid in self._index.crawlers:
            info = self._index.crawlers[sid]
        else:
            logger.info(f"Found non-indexed crawler: {crawler.__name__}")
            info = utils.create_crawler_info(crawler)
            self._index.crawlers[sid] = info

        # update crawlers list with the latest crawler
        def _set(key: str):
            if key in self.crawlers:
                if version < getattr(self.crawlers[key], "version"):
                    return  # skip if current crawler is the latest
            self.crawlers[key] = crawler

        _set(sid)
        for url in urls:
            _set(extract_host(url))

        # add keys for searching
        self._store.insert(sid, sid)
        self._store.insert(normalize(file), sid)
        self._store.insert(normalize(crawler.__name__), sid)
        for url in urls:
            self._store.insert(normalize_url(url), sid)
        return info

    def update(self) -> None:
        assert self._index
        logger.info("Sync online sources")
        online_index = utils.fetch_online_source()
        if online_index.v <= self._index.v:
            logger.info("No latest updates found")
            return

        # save the latest index
        user_file = ctx.config.crawler.user_index_file
        utils.save_source(user_file, self._index)

        # load the online index
        self.load_index(online_index)

        # download updated source files
        futures = []
        for id, source in online_index.crawlers.items():
            current = self._index.crawlers.get(id)
            if current and current.version >= source.version:
                continue
            user_sources = ctx.config.crawler.user_sources.parent
            dst_file = (user_sources / source.file_path).resolve()
            f = self._taskman.submit_task(ctx.http.download, source.url, dst_file)
            futures.append(f)

        # wait for completion
        for dst_file in self._taskman.resolve_as_generator(
            futures,
            desc="Downloading",
            unit="source",
            signal=self._signal,
        ):
            if dst_file:
                self.load_crawlers(dst_file)
        logger.info("Source synced.")

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
        if not self._index:
            raise ServerErrors.source_not_loaded

        if query:
            query = normalize(query)
            ids = self._store.search(query)
            infos = [self._index.crawlers[id] for id in ids]
        else:
            infos = list(self._index.crawlers.values())

        result: List[SourceItem] = []
        for info in infos:
            crawler = self.crawlers.get(info.id)
            if not crawler:
                continue

            if can_search is not None and info.can_search != can_search:
                continue
            if can_login is not None and info.can_login != can_login:
                continue
            if has_mtl is not None and info.has_mtl != has_mtl:
                continue
            if has_manga is not None and info.has_manga != has_manga:
                continue

            urls = info.base_urls
            if query:
                urls = [url for url in info.base_urls if query in normalize(url)] or info.base_urls

            language = info.file_path.split("/")[1]
            for url in urls:
                domain = extract_host(url)
                is_disabled = domain in self.rejected
                if not include_rejected and is_disabled:
                    continue

                item = SourceItem(
                    url=url,
                    domain=domain,
                    language=language,
                    version=info.version,
                    has_manga=info.has_manga,
                    has_mtl=info.has_mtl,
                    is_disabled=is_disabled,
                    disable_reason=self.rejected.get(domain, "No reason provided"),
                    can_search=info.can_search,
                    can_login=info.can_login,
                    total_commits=info.total_commits,
                    contributors=info.contributors,
                    # Excluded fields
                    info=info,
                    crawler=crawler,
                )
                result.append(item)
        return result

    def get_info(self, query: str) -> Optional[CrawlerInfo]:
        if query in self._index.crawlers:
            return self._index.crawlers[query]
        elif query in self.crawlers:
            id = getattr(self.crawlers[query], "__id__")
            return self._index.crawlers[id]
        else:
            ids = self._store.search(normalize(query))
            if len(ids) != 1:
                return None
            return self._index.crawlers[ids[0]]

    def get_crawler(self, url: str) -> Type[Crawler]:
        self.ensure_load()
        if not self._index:
            raise ServerErrors.source_not_loaded

        host = extract_host(url)
        if not host:
            raise ServerErrors.invalid_url
        if host in self.rejected:
            raise ServerErrors.host_rejected.with_extra(self.rejected[host])
        if host not in self.crawlers:
            raise ServerErrors.no_crawler.with_extra(host)

        constructor = self.crawlers[host]
        setattr(constructor, "url", url)
        return constructor

    def init_crawler(
        self,
        constructor: Type[Crawler],
        disable_logger=not ctx.logger.is_debug,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
    ) -> Crawler:
        url = getattr(constructor, "url")
        logger.debug(f"Creating crawler instance for {url}")

        # disable logging
        if disable_logger:
            module = getattr(constructor, "__module_obj__")
            setattr(module, "print", lambda *a, **k: None)
            setattr(
                module, "logger", type("", (), {"__getattr__": lambda *n: lambda *a, **k: None})()
            )

        # create instance
        crawler = constructor(
            origin=url,
            workers=workers,
            parser=parser,
        )
        crawler.initialize()
        return crawler
