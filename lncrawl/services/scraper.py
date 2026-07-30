from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..config import APP_DIR
from ..context import ctx
from ..utils.url_tools import extract_base

if TYPE_CHECKING:
    from scraper import ExitSpec, Memory, Scraper, ScraperConfig, SharedState

logger = logging.getLogger(__name__)


class ScraperService:
    """The only place a `Scraper` is constructed.

    Everything keyed by origin — the pacing clock, the held address, the identity built
    on it, the referrer chain and what has been learned — lives in one process-wide
    `SharedState`, because those describe the *site* rather than any one crawler. Two
    crawlers with separate state do not look like one visitor going faster; they look
    like two who contradict each other, and each flush of a second `Memory` over the
    same file erases what the first learned.

    Two traffic shapes, and they genuinely differ. Crawl traffic is paced, remembered
    and routed through the configured exits. Non-crawl traffic — our own Calibre and
    translator APIs, the GitHub source index, favicons — is none of those things, so it
    gets a scraper that neither waits nor remembers.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._memory: Optional["Memory"] = None
        self._state: Optional["SharedState"] = None
        self._plain: Optional["Scraper"] = None

    # ------------------------------------------------------------------------- #
    # Configuration
    # ------------------------------------------------------------------------- #

    def _exits(self) -> List["ExitSpec"]:
        """Translate `crawler.proxy_urls` into the scraper's exit list.

        The scraper describes an address by *kind* rather than by URL, because what a
        detector reads is the reputation of the range it belongs to — a datacenter proxy
        and a residential one are not interchangeable however similar the URL looks. Kinds
        are inferred here from the only thing the config carries, so a datacenter guess is
        the conservative default: it never claims reach the address does not have.

        `allow_fallback_on_proxy_miss` becomes a direct entry in the list. The scraper
        dropped its own fallback-to-direct switch — silently leaving the proxy is how a
        scrape leaks the host's real address mid-session — but an operator who asked for
        that behaviour is asking for direct to be *an option*, and an exit list is exactly
        how you say so.
        """
        from scraper import ExitKind, ExitSpec, TorPoolSpec

        if not ctx.config.crawler.enable_proxy:
            return []

        exits: List[ExitSpec] = []
        for entry in ctx.config.crawler.proxy_urls.split(","):
            entry = entry.strip()
            if not entry:
                continue
            if entry.startswith("torpool;"):
                # torpool;<api_url>;<socks_url>;<token>
                parts = entry.split(";")
                socks = parts[2] if len(parts) > 2 and parts[2] else "socks5h://127.0.0.1:9250"
                exits.append(
                    TorPoolSpec(
                        url=socks,
                        api_url=parts[1],
                        token=parts[3] if len(parts) > 3 else "",
                    )
                )
            elif entry.startswith("tor;"):
                # Legacy form: tor;<host>;<port>;<control_port>;<control_password>.
                # The control port is accepted and ignored. Rotation by NEWNYM is gone —
                # it has a ~10s cooldown and gives no say in which exit comes next, so a
                # rotation could land on the same relay. tor-pool reassigns instead, which
                # is what `torpool;` is for.
                parts = entry.split(";")
                host = parts[1] if len(parts) > 1 else "127.0.0.1"
                port = parts[2] if len(parts) > 2 else "9050"
                exits.append(ExitSpec(url=f"socks5h://{host}:{port}", kind=ExitKind.TOR))
            else:
                exits.append(ExitSpec(url=entry, kind=ExitKind.DATACENTER))

        if exits and ctx.config.crawler.allow_fallback_on_proxy_miss:
            exits.append(ExitSpec(url="", kind=ExitKind.DIRECT, label="direct"))
        return exits

    def _crawl_settings(self) -> Dict[str, Any]:
        """The settings that describe crawl traffic, shared state included."""
        return {
            "exits": self._exits(),
            "data_dir": APP_DIR / "scraper",
            # lncrawl crawls a curated list of novel sites, not an open frontier, so
            # AI-labyrinth decoys are not its threat model and a false positive costs a
            # job for no corresponding gain.
            "guard_topic": False,
        }

    def _crawl_config(
        self,
        *,
        parser: Optional[str] = None,
        warmup: bool = True,
        raise_for_status: bool = True,
    ) -> "ScraperConfig":
        from scraper import PacingPolicy, ScraperConfig

        settings = self._crawl_settings()
        settings["raise_for_status"] = raise_for_status
        settings["pacing"] = PacingPolicy(warmup=warmup)
        if parser:
            settings["parser"] = parser
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
        if state is not None:
            state.exits.release_all()
        if plain is not None:
            self._close(plain)

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
    ) -> "Scraper":
        """A scraper for crawl traffic against *origin*, sharing the process state.

        *rate_limit* is the source's declared requests per second. It seeds this
        origin's clock and is superseded by anything already learned about the site: a
        throttle observed on a previous run is a measurement, and this is a guess.
        """
        from scraper import Scraper

        state = self.state
        scraper = Scraper(
            origin=origin or "",
            parser=parser,
            config=self._crawl_config(
                parser=parser,
                warmup=warmup,
                raise_for_status=raise_for_status,
            ),
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
        scraper = self.open(extract_base(url))
        try:
            return scraper.explain(url)
        finally:
            self._close(scraper)

    # ------------------------------------------------------------------------- #
    # Teardown
    # ------------------------------------------------------------------------- #

    @staticmethod
    def _close(scraper: "Scraper") -> None:
        try:
            scraper.close()
        except Exception:
            logger.debug("Error closing scraper", exc_info=True)

    def close(self) -> None:
        with self._lock:
            plain, self._plain = self._plain, None
            state, self._state = self._state, None
            memory, self._memory = self._memory, None
        if plain is not None:
            self._close(plain)
        if state is not None:
            state.exits.release_all()
        if memory is not None:
            memory.close()
