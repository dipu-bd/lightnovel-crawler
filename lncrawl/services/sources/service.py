import asyncio
import logging
from pathlib import Path
from threading import Event, Thread
import traceback
from typing import Dict, List, Optional, Type
from urllib.parse import urlsplit

from scraper import LAYERS, extract_host

from ...context import ctx
from ...core import Crawler
from ...core.tiers import LEGACY, TIERS, describe, outranks
from ...exceptions import AbortedException, ServerError, ServerErrors
from ...server.models import CrawlerIndex, CrawlerInfo, SourceDiagnosis, SourceItem
from ...utils.event_lock import EventLock
from ...utils.fts_store import FTSStore
from ...utils.text_tools import normalize
from ...utils.url_tools import normalize_url
from . import spec_tier
from .helper import (
    batch_import,
    create_crawler_info,
    create_source_item,
    load_offline_source,
    save_source,
)
from .spec_tier import load_specs
from .tester import run_crawler_test

logger = logging.getLogger(__name__)


class Sources:
    def __init__(self) -> None:
        self._signal: Event
        self._loader: Thread
        self._store: FTSStore
        self._index: CrawlerIndex
        self._sync_lock: EventLock
        self.rejected: Dict[str, str] = {}  # Map of host -> rejection reason
        self.crawlers: Dict[str, Type[Crawler]] = {}  # Map of cid -> crawler
        self.info: Dict[str, CrawlerInfo] = {}  # Map of cid -> crawler info
        self.sources: Dict[str, SourceItem] = {}  # Map of host -> source item

    @property
    def version(self) -> int:
        if not hasattr(self, "_index"):
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
        if hasattr(self, "_index"):
            del self._index
        self.rejected.clear()
        self.sources.clear()
        self._sync_lock.abort()

    def ensure_load(self):
        try:
            if hasattr(self, "_loader") and isinstance(self._loader, Thread):
                self._loader.join()
        except AbortedException:
            pass
        finally:
            if hasattr(self, "_loader"):
                delattr(self, "_loader")

    def load(self, sync_remote=True):
        self._signal = Event()
        self._store = FTSStore()
        self._sync_lock = EventLock()

        def loader():
            # load offline sources first
            self.load_index(load_offline_source(sync_remote))

            # check online sources update
            if sync_remote:
                self.update()

        self._loader = Thread(target=loader, daemon=True)
        self._loader.start()

    def update(self, ignore_cache=False) -> None:
        try:
            with self._sync_lock:
                if self._signal.is_set():
                    return

                logger.info(f"Sync online sources (current={self.version})")
                online_index = ctx.github.fetch_online_source(ignore_cache)
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
                    if self._signal.is_set():
                        return
                    current = self._index.crawlers.get(id)
                    if current and current.version >= source.version:
                        continue
                    try:
                        ctx.github.download_online_source(source.file_path)
                        logger.debug(f"Downloaded source: {source.file_path}")
                    except Exception:
                        logger.warning(
                            f"Failed to download source: {source.file_path}",
                            exc_info=ctx.logger.is_info,
                        )

            # load the online index
            self.load_index(online_index)
            logger.info("Source synced.")
        except AbortedException:
            pass

    def load_index(self, index: CrawlerIndex) -> None:
        try:
            with self._sync_lock:
                if self._signal.is_set():
                    return

                # set the index
                self._index = index

                # update rejected list
                self.rejected.clear()
                for url, reason in index.rejected.items():
                    host = extract_host(url)
                    self.rejected[host] = reason

                # import legacy crawlers (TODO: to be discontinued)
                self.info.clear()
                self.crawlers.clear()
                self.sources.clear()
                self.load_crawlers(
                    *ctx.config.crawler.local_sources.glob("**/*.py"),
                    *ctx.config.crawler.user_sources.glob("**/*.py"),
                )

                # load the new specs tier
                self.load_specs()

                self.log_tier_tally()
        except AbortedException:
            pass

    def load_crawlers(self, *files: Path):
        for crawler in batch_import(*files):
            if self._signal.is_set():
                return
            self.add_crawler(crawler)

    def load_specs(self):
        """Register the spec tier, if there is one.

        Silent when the definitions directory or the interpreter is absent, which is the state
        every checkout is in until both exist. lncrawl then behaves exactly as it did before.
        """
        for crawler in load_specs(ctx.config.crawler.spec_sources).values():
            if self._signal.is_set():
                return
            self.add_crawler(crawler)

    def log_tier_tally(self):
        """How many hosts each tier ended up serving.

        A spec tier that failed to load is otherwise indistinguishable from one that was never
        configured: both simply leave the legacy crawlers in place.
        """
        tally = {tier: 0 for tier in TIERS}
        for item in self.sources.values():
            tally[item.tier] = tally.get(item.tier, 0) + 1
        logger.info(
            "Sources by tier: %s",
            ", ".join(f"{count} {tier}" for tier, count in tally.items()),
        )
        # Said out loud rather than left to the per-file warnings. A spec that failed to load
        # leaves its host on the legacy crawler, which looks exactly like a host that never had
        # one: an interpreter a minor version too old once hid 36 of them that way.
        if spec_tier.unreadable:
            logger.warning(
                "%d spec(s) could not be read and their hosts fell back to a legacy crawler",
                spec_tier.unreadable,
            )

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

        tier = getattr(crawler, "tier", LEGACY)

        # skip this crawler if something already registered outranks it
        current = self.crawlers.get(cid)
        if current is not None and not outranks(
            tier, info.version, getattr(current, "tier", LEGACY), self.info[cid].version
        ):
            return
        self.info[cid] = info
        self.crawlers[cid] = crawler

        # load source items
        for url in crawler.base_url:
            if self._signal.is_set():
                return
            self.add_source(url, info, tier, getattr(crawler, "updated_at", None))

    def add_source(
        self,
        url: str,
        info: CrawlerInfo,
        tier: str = LEGACY,
        updated_at: Optional[int] = None,
    ):
        item = create_source_item(url, info, self.rejected, tier, updated_at)

        # Tier first, version only within a tier. Comparing versions alone would let a legacy
        # crawler re-downloaded by the sync outrank the spec meant to replace it: a legacy
        # version is a file timestamp and the download refreshes it.
        existing = self.sources.get(item.domain)
        if existing is not None and not outranks(
            item.tier, item.version, existing.tier, existing.version
        ):
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
                    has_mtl is None or item.has_mtl is has_mtl,
                    has_manga is None or item.has_manga is has_manga,
                    can_login is None or item.can_login is can_login,
                    can_search is None or item.can_search is can_search,
                    include_rejected or not item.is_disabled,
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

    def diagnose(self, domain: str) -> SourceDiagnosis:
        """Why *domain* is or is not working.

        Reports a rejection rather than refusing on one, unlike every crawl path — a
        rejected host is the one whose diagnosis is most worth reading — and answers
        for a rejected host that has no crawler at all, which is most of them.
        """
        self.ensure_load()
        if domain.startswith("www."):
            domain = domain[4:]
        rejected = self.rejected.get(domain)
        source = self.sources.get(domain)
        if source is None and rejected is None:
            raise ServerErrors.no_crawler.with_extra(domain)

        url = source.url if source else f"https://{domain}/"
        health = ctx.health.reasons(domain)
        result = SourceDiagnosis(
            domain=domain,
            url=url,
            rejected=rejected,
            is_disabled=source.is_disabled if source else True,
            disable_reason=source.disable_reason if source else rejected,
            health=health,
            samples={reason: ctx.health.samples(domain, reason) for reason in health},
            explain=ctx.scraper.explain(url),
        )

        profile = ctx.scraper.knows(url)
        if profile is None:
            return result

        result.known = True
        result.tier = profile.tier
        result.interval = profile.interval
        result.successes = profile.successes
        result.failures = profile.failures
        result.consecutive_failures = profile.consecutive_failures
        result.has_clearance = profile.clearance_for(url) is not None

        layer = profile.binding
        if layer is not None:
            facts = LAYERS[layer]
            result.binding_layer = int(layer)
            result.binding_layer_name = str(layer)
            result.reads = facts.trait.value
            result.stance = facts.stance.value
            result.summary = facts.summary
        return result

    def get_crawler(self, domain: str) -> Type[Crawler]:
        source = self.get_source(domain)
        return self.crawlers[source.crawler_id]

    def find_crawler(self, url: str) -> Type[Crawler]:
        self.ensure_load()
        return self.get_crawler(self.get_domain(url))

    def init_crawler(
        self,
        url: str,
        parser: Optional[str] = None,
        timeout: Optional[float] = None,
        probe: bool = False,
    ) -> Crawler:
        domain = self.get_domain(url)
        try:
            source = self.get_source(domain)
        except ServerError:
            if not ctx.config.crawler.generic_fallback:
                raise
            return self._init_generic(url, domain, parser, timeout, probe)

        cid = source.crawler_id
        constructor = self.crawlers[cid]

        # create instance
        ctx.logger.debug(
            f"Creating crawler instance for {url}: {describe(source.tier, source.file_path)}"
        )
        open_session = ctx.scraper.probe if probe else ctx.scraper.open
        crawler = constructor(
            origin=source.url,
            parser=parser,
            scraper=open_session(
                source.url,
                parser=parser,
                rate_limit=constructor.request_rate_limit,
                timeout=timeout,
            ),
        )

        if not crawler.language:
            crawler.language = source.language

        crawler.initialize()
        return crawler

    def _init_generic(
        self,
        url: str,
        domain: str,
        parser: Optional[str],
        timeout: Optional[float],
        probe: bool,
    ) -> Crawler:
        """Read a site nobody has written a crawler for, by guessing its structure.

        Deliberately not registered as a source: it has no `base_url`, answers for any
        host, and must never be mistaken for one that has been verified against the site.
        """
        from ...templates.generic import GenericCrawler

        origin = f"{urlsplit(url).scheme or 'https'}://{urlsplit(url).netloc}/"
        ctx.logger.warn(f"No crawler for {domain}, guessing the page structure")
        open_session = ctx.scraper.probe if probe else ctx.scraper.open
        crawler = GenericCrawler(
            origin=origin,
            parser=parser,
            scraper=open_session(
                origin,
                parser=parser,
                rate_limit=GenericCrawler.request_rate_limit,
                timeout=timeout,
            ),
        )
        crawler.initialize()
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

        Thread(target=run, daemon=True).start()

        while True:
            item = await queue.get()
            if event.is_set() and item == "END\n":
                break
            yield item
