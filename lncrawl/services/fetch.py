from contextlib import contextmanager
import hashlib
import logging
from pathlib import Path
import shutil
from threading import Event, Lock, Thread, current_thread
from typing import Dict, Optional

from scraper import Scraper

from ..assets.images import favicon_icon
from ..context import ctx
from ..utils.url_tools import extract_base

logger = logging.getLogger(__name__)


class FetchService:
    """Shared HTTP client for non-crawl traffic (translator service, Calibre
    API, favicons, source index).

    Each thread gets its own `Scraper`, which already throttles and
    concurrency-limits itself, so this service adds no lock of its own and a
    job's abort `signal` never bleeds into another thread's. Source crawling
    is unaffected — each crawler owns a separate scraper.
    """

    def __init__(self) -> None:
        self._scrapers: Dict[Thread, Scraper] = {}
        self._lock = Lock()

    def _scraper(self) -> Scraper:
        thread = current_thread()
        with self._lock:
            scraper = self._scrapers.get(thread)
            if scraper is None:
                self._reap()
                scraper = self._scrapers[thread] = Scraper()
            return scraper

    def _reap(self) -> None:
        for thread in [t for t in self._scrapers if not t.is_alive()]:
            self._close(self._scrapers.pop(thread))

    @staticmethod
    def _close(scraper: Scraper) -> None:
        try:
            scraper.close()
        except Exception:
            logger.debug("Error closing scraper", exc_info=True)

    def close(self):
        with self._lock:
            scrapers = list(self._scrapers.values())
            self._scrapers.clear()
        for scraper in scrapers:
            self._close(scraper)

    @contextmanager
    def session(self, signal: Optional[Event] = None):
        scraper = self._scraper()
        original_signal = scraper.signal
        if signal is not None:
            scraper.signal = signal
        try:
            yield scraper
        finally:
            scraper.signal = original_signal

    def get(
        self,
        url: str,
        signal: Optional[Event] = None,
    ) -> bytes:
        with self.session(signal) as sess:
            resp = sess.get(url)
            resp.raise_for_status()
            return resp.content

    def download(
        self,
        url: str,
        file: Path,
        signal: Optional[Event] = None,
    ) -> None:
        with self.session(signal) as sess:
            sess.get_file(url, output_file=file)
        logger.debug(f"Downloaded: {file}")

    def favicon(
        self,
        url: str,
        signal: Optional[Event] = None,
    ) -> Path:
        favicon_url = f"{extract_base(url)}favicon.ico"

        filename = hashlib.md5(favicon_url.encode()).hexdigest()
        out_file = ctx.files.resolve(f"images/{filename}.ico")
        if out_file.is_file():
            return out_file

        try:
            self.download(favicon_url, out_file, signal)
        except Exception:
            logger.info(f"Failed to download favicon: {url}")
            shutil.copy(favicon_icon(), out_file)

        return out_file
