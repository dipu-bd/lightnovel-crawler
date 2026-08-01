from __future__ import annotations

from importlib import util
import logging
import threading
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from scraper import BROWSER_MODES, extract_base, pick_chromium, pick_firefox

from ..config import APP_DIR
from ..context import ctx
from ..utils import proxy_tools
from ..utils.proxy_tools import ProxyExit, ProxyKind

if TYPE_CHECKING:
    from scraper import (
        BrowserSolver,
        ExitSpec,
        Memory,
        OriginProfile,
        Scraper,
        ScraperConfig,
        SharedState,
    )

logger = logging.getLogger(__name__)


class ScraperService:
    """The only place a `Scraper` is constructed.

    Everything keyed by origin — the pacing clock, the held address, the identity built
    on it, the referrer chain and what has been learned — lives in one process-wide
    `SharedState`, because those describe the *site* rather than any one crawler. Two
    crawlers with separate state do not look like one visitor going faster; they look
    like two who contradict each other, and each flush of a second `Memory` over the
    same file erases what the first learned.

    Three traffic shapes, and they genuinely differ. Crawl traffic is paced, remembered
    and routed through the configured exits, and it is worth being patient with because
    the session goes on to fetch a book. A probe — the search fan-out — asks one question
    of many sites at once and throws every session away, so patience there buys nothing
    and costs the caller its deadline. Non-crawl traffic — our own Calibre and translator
    APIs, the GitHub source index, favicons — neither waits nor remembers.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._memory: Optional["Memory"] = None
        self._state: Optional["SharedState"] = None
        self._plain: Optional["Scraper"] = None
        self._solver: Optional["BrowserSolver"] = None
        self._solver_ready = False

    # ------------------------------------------------------------------------- #
    # Configuration
    # ------------------------------------------------------------------------- #

    def _exits(self) -> List["ExitSpec"]:
        """Hand `crawler.proxies` to the scraper as its exit list."""
        from scraper import ExitKind, ExitSpec, TorPoolSpec

        if not ctx.config.crawler.enable_proxy:
            return []

        exits: List[ExitSpec] = []
        for proxy in ctx.config.crawler.proxies:
            if not proxy.enabled:
                continue
            if proxy.kind is ProxyKind.torpool:
                exits.append(
                    TorPoolSpec(
                        url=proxy.url,
                        api_url=proxy.api_url,
                        token=proxy.token,
                        label=proxy.label,
                    )
                )
            else:
                exits.append(
                    ExitSpec(
                        url=proxy.url,
                        kind=ExitKind(proxy.kind.value),
                        label=proxy.label,
                    )
                )

        if exits and ctx.config.crawler.allow_fallback_on_proxy_miss:
            exits.append(ExitSpec(url="", kind=ExitKind.DIRECT, label="direct"))
        return exits

    @property
    def solver(self) -> Optional["BrowserSolver"]:
        """The one browser this process will drive, or None.

        One instance because solving serialises on the solver's own lock: two headed
        browsers sharing a profile directory corrupt it, and that profile is what carries
        the accumulated history a solve depends on.

        Gated on a browser actually being installed as well as on the setting. The
        setting defaults to on and an image need not ship a browser, and a solver that
        cannot launch spends the whole solve timeout per challenged origin before
        reporting the timeout as though the site had blocked us.
        """
        with self._lock:
            # A resolved `None` means "no browser here", which is not the same as "not
            # asked yet" — so the answer is cached with a flag rather than by its value.
            if not self._solver_ready:
                self._solver = self._build_solver()
                self._solver_ready = True
            return self._solver

    def _build_solver(self) -> Optional["BrowserSolver"]:
        if not ctx.config.crawler.can_use_browser:
            logger.info("Browser crawling is disabled in the configuration")
            return None

        # Both solvers talk their protocol over a WebSocket
        if not util.find_spec("websockets"):
            logger.info("The websockets package is missing; challenges will not be solved")
            return None

        # Normalised: an unrecognised value here would silently mean "chrome"
        wanted = (ctx.config.crawler.browser_driver or "").strip().lower()
        if wanted not in ("auto", "firefox", "chrome"):
            logger.warning("Unknown browser_driver %r; using auto", wanted)
            wanted = "auto"
        # Normalised for the same reason: the scraper rejects an unknown mode outright,
        # and a value written straight into config.json never passed the setter
        mode = (ctx.config.crawler.browser_mode or "").strip().lower()
        if mode not in BROWSER_MODES:
            logger.warning("Unknown browser_mode %r; using auto", mode)
            mode = "auto"

        # Firefox first as that reaches the most sites
        if wanted in ("auto", "firefox"):
            firefox = pick_firefox()
            if firefox:
                from scraper import BidiSolver

                return BidiSolver(executable=firefox, mode=mode)
            if wanted == "firefox":
                logger.info("No Firefox executable found; challenges will not be solved")
                return None

        chromium = pick_chromium()
        if chromium:
            from scraper import CdpSolver

            return CdpSolver(executable=chromium, mode=mode)

        logger.info("No browser executable found; challenges will not be solved")
        return None

    def _crawl_settings(self) -> Dict[str, Any]:
        """The settings that describe crawl traffic, shared state included."""
        crawler = ctx.config.crawler
        settings: Dict[str, Any] = {
            "exits": self._exits(),
            "data_dir": APP_DIR / "scraper",
            "browser": self.solver,
            # lncrawl crawls a curated list of novel sites, not an open frontier, so
            # AI-labyrinth decoys are not its threat model and a false positive costs a
            # job for no corresponding gain.
            "guard_topic": False,
            "max_sessions_per_exit": crawler.max_sessions_per_exit,
            "max_attempts": crawler.max_attempts,
            "max_rotations": crawler.max_rotations,
            "solve_timeout": crawler.solve_timeout,
            "archive": crawler.use_archive,
            "archive_max_age": crawler.archive_max_age,
        }
        if crawler.impersonate:
            settings["impersonate"] = crawler.impersonate
        return settings

    def _crawl_config(
        self,
        *,
        parser: Optional[str] = None,
        warmup: bool = True,
        raise_for_status: bool = True,
        timeout: Optional[float] = None,
        probe: bool = False,
    ) -> "ScraperConfig":
        from scraper import PacingPolicy, ScraperConfig

        settings = self._crawl_settings()
        settings["raise_for_status"] = raise_for_status
        if parser:
            settings["parser"] = parser
        if timeout:
            settings["timeout"] = (timeout, timeout)
        if probe:
            settings["browser"] = None
            settings["archive"] = False
            settings["max_attempts"] = 1
            settings["max_rotations"] = 0
            warmup = False
        settings["pacing"] = PacingPolicy(warmup=warmup)
        return ScraperConfig(**settings)

    def _plain_config(self) -> "ScraperConfig":
        from scraper import PacingPolicy, ScraperConfig

        return ScraperConfig(
            remember=False,
            guard_topic=False,
            browser=None,
            pacing=PacingPolicy(interval=0.0, floor=0.0, warmup=False),
        )

    # ------------------------------------------------------------------------- #
    # Shared state
    # ------------------------------------------------------------------------- #

    @property
    def memory(self) -> "Memory":
        """The one store of what has been learned, for the life of the process.

        Never rebuilt, even when the configuration changes: each store holds every
        origin it knows and a flush writes all of them, so a second store over the same
        file does not merge with the first — the later write is the whole file.
        """
        with self._lock:
            if self._memory is None:
                from scraper import Memory

                self._memory = Memory(self._crawl_config().memory_path)
            return self._memory

    @property
    def state(self) -> "SharedState":
        with self._lock:
            if self._state is None:
                from scraper import SharedState

                self._state = SharedState.create(self._crawl_config(), memory=self.memory)
            return self._state

    def invalidate(self) -> None:
        """Rebuild the shared state on next use, after the configuration changed.

        The exits and the pacing policy are read once when the state is built, so an
        operator changing the proxy list needs the pool rebuilt. Crawlers already
        holding a scraper keep the old state until they close, which is why the memory
        outlives this and is handed to the replacement.
        """
        with self._lock:
            state, self._state = self._state, None
            plain, self._plain = self._plain, None
            solver, self._solver = self._solver, None
            self._solver_ready = False
        if state is not None:
            state.exits.release_all()
        if plain is not None:
            self._close(plain)
        if solver is not None:
            self._close_solver(solver)

    # ------------------------------------------------------------------------- #
    # Sessions
    # ------------------------------------------------------------------------- #

    def open(
        self,
        origin: Optional[str] = None,
        *,
        parser: Optional[str] = None,
        rate_limit: float = 0.0,
        warmup: bool = True,
        raise_for_status: bool = True,
        timeout: Optional[float] = None,
    ) -> "Scraper":
        """A scraper for crawl traffic against *origin*, sharing the process state.

        *rate_limit* is the source's declared requests per second. It seeds this
        origin's clock and is superseded by anything already learned about the site: a
        throttle observed on a previous run is a measurement, and this is a guess.

        *timeout* bounds a single request, connect and read alike. Worth choosing rather
        than inheriting wherever a caller has a deadline of its own: the default read
        budget is minutes, an abort signal cannot interrupt a blocking socket read, and
        the pool's threads are joined at interpreter exit — so one stalled host holds a
        command open long after its results are on screen.
        """
        return self._session(
            origin,
            rate_limit,
            self._crawl_config(
                parser=parser,
                warmup=warmup,
                raise_for_status=raise_for_status,
                timeout=timeout,
            ),
        )

    def probe(
        self,
        origin: Optional[str] = None,
        *,
        parser: Optional[str] = None,
        rate_limit: float = 0.0,
        timeout: Optional[float] = None,
    ) -> "Scraper":
        """A scraper for one throwaway question against *origin*.

        Everything the crawl config spends to see a request through is worth nothing
        here, because the answer is a list of titles and the session is discarded the
        moment it arrives. So: one attempt rather than five, no rotation, and no
        challenge solving at all — a clearance earned in the browser is thrown away with
        the session holding it, and solving serialises on one lock, so a fan-out across
        many sites queues behind whichever of them is challenged. No warm-up either: it
        doubles the requests to build a session nothing reuses.

        The web archive is off here even where it is on for crawling. It exists to rescue
        a page that a site will not give up, and no snapshot answers a query string the
        archive has never been asked for — so every lookup is a slow index query that
        cannot succeed.

        Shares the process state regardless, so a probe still paces itself against what
        a crawl has already learned about the same site.
        """
        return self._session(
            origin,
            rate_limit,
            self._crawl_config(parser=parser, timeout=timeout, probe=True),
        )

    def _session(
        self,
        origin: Optional[str],
        rate_limit: float,
        config: "ScraperConfig",
    ) -> "Scraper":
        from scraper import Scraper

        state = self.state
        scraper = Scraper(
            origin=origin or "",
            parser=config.parser,
            config=config,
            state=state,
        )
        if origin and rate_limit > 0:
            state.pacer.learn(state.memory.key(origin), 1.0 / rate_limit)
        return scraper

    def plain(self) -> "Scraper":
        """The shared scraper for non-crawl traffic.

        One for the process rather than one per thread: with a per-request abort signal
        there is no per-scraper state left for a thread to own.
        """
        with self._lock:
            if self._plain is None:
                from scraper import Scraper

                self._plain = Scraper(config=self._plain_config())
            return self._plain

    def set_rate_limit(self, url: str, requests_per_second: float) -> None:
        """Pace *url*'s origin at this rate, for this run and every later one.

        Written to the memory rather than to the clock because a fetch re-seeds the
        clock from what is remembered about the origin, so a value set only on the
        pacer is overwritten by the first request.
        """
        if requests_per_second <= 0:
            return
        interval = 1.0 / requests_per_second
        state = self.state
        state.memory.profile(url).interval = interval
        state.memory.touch()
        state.pacer.learn(state.memory.key(url), interval)

    def unchanged(self, url: str, signal: Optional[Any] = None) -> bool:
        """True when *url* answers 304 to the validators last seen for it.

        False whenever nothing is known, so a caller that skips work on the strength of
        this never skips it for an endpoint that was never recorded.
        """
        scraper = self.open(
            extract_base(url),
            warmup=False,
            raise_for_status=False,
        )
        try:
            return scraper.unchanged(url, signal=signal)
        except Exception:
            logger.debug(f"Could not revalidate {url}", exc_info=True)
            return False
        finally:
            self._close(scraper)

    def explain(self, url: str) -> str:
        """The scraper's own account of *url*'s origin, without recording one.

        `Scraper.explain` reads the origin through `Memory.profile`, which mints a
        profile on a miss — so asking about an origin is enough to store one. That
        turns a status page into a writer, and with the store bounded it can evict a
        profile a crawl is relying on, so an origin nothing was known about is left
        that way.
        """
        known = self.knows(url) is not None
        scraper = self.open(extract_base(url))
        try:
            return scraper.explain(url)
        finally:
            if not known:
                self.memory.forget(url)
            self._close(scraper)

    def proxies(self) -> List[Dict[str, Any]]:
        """Every configured proxy, with what it is doing right now.

        The address half of `explain()`, and the only view of it there is: which exits
        the pool has retired and when they come back is otherwise visible only in debug
        logs, so an operator whose scrape has slowed has nothing to look at.

        Status is joined onto the configuration rather than served beside it, because a
        proxy and its health are one thing to whoever is looking. A disabled entry is
        listed and simply has no status — it is not in the pool.

        `clears_reputation` is derived rather than stored: it is the one thing the kind
        is *for*, and the reason declaring it correctly matters.
        """
        from scraper import ExitKind, Layer

        configured = ctx.config.crawler.proxies
        live = {item.name: item for item in self.state.exits.status()}

        out: List[Dict[str, Any]] = []
        for proxy in configured:
            row = proxy_tools.public(proxy)
            kind = ExitKind.TOR if proxy.kind is ProxyKind.torpool else ExitKind(proxy.kind.value)
            row["clears_reputation"] = Layer.IP_REPUTATION in kind.reach
            status = live.get(proxy.name)
            row["retired"] = bool(status and status.retired)
            row["returns_in"] = status.returns_in if status else 0.0
            row["origins"] = status.origins if status else 0
            out.append(row)
        return out

    def set_proxies(self, submitted: List["ProxyExit"]) -> List[Dict[str, Any]]:
        """Replace the configured proxies, keeping any secret that was not re-sent.

        Rebuilds the shared state, because the exit list is read once when the pool is
        built — an operator who just added an address expects the next request to use it.
        """
        merged = proxy_tools.merge_secrets(submitted, ctx.config.crawler.proxies)
        ctx.config.crawler.proxies = merged
        ctx.config.save()
        self.invalidate()
        return self.proxies()

    def knows(self, url: str) -> Optional["OriginProfile"]:
        """What has been learned about *url*'s origin, or None if nothing has.

        Deliberately not `Memory.profile`, which mints a profile on a miss and marks
        the store dirty: a read-only status view must not be able to write one origin
        per domain an operator happens to look at.
        """
        memory = self.memory
        key = memory.key(url)
        for profile in memory.profiles():
            if profile.origin == key:
                return profile
        return None

    # ------------------------------------------------------------------------- #
    # Teardown
    # ------------------------------------------------------------------------- #

    @staticmethod
    def _close(scraper: "Scraper") -> None:
        try:
            scraper.close()
        except Exception:
            logger.debug("Error closing scraper", exc_info=True)

    @staticmethod
    def _close_solver(solver: "BrowserSolver") -> None:
        try:
            solver.close()
        except Exception:
            logger.debug("Error closing browser solver", exc_info=True)

    def close(self) -> None:
        with self._lock:
            plain, self._plain = self._plain, None
            state, self._state = self._state, None
            memory, self._memory = self._memory, None
            solver, self._solver = self._solver, None
            self._solver_ready = False
        if plain is not None:
            self._close(plain)
        if state is not None:
            state.exits.release_all()
        if memory is not None:
            memory.close()
        if solver is not None:
            self._close_solver(solver)
