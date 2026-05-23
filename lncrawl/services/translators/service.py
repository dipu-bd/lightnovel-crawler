from hashlib import sha256
import logging
from threading import Event
import time
from typing import Dict, Generator, Iterable, List, Optional, Tuple, Union

import sqlmodel as sq

from ...context import ctx
from ...dao.chapter import ChapterTranslation
from ...exceptions import ServerErrors
from .backend_baidu import BaiduTranslate
from .backend_base import BackendBase
from .backend_bing import BingTranslate
from .backend_google import GoogleClient5Translate, GoogleGtxTranslate, GoogleMobileTranslate
from .backend_lingva import LingvaTranslate
from .languages import LanguageCode

logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self) -> None:
        self._failing: Dict[BackendBase, float] = {}
        self._backends: List[BackendBase] = [
            BingTranslate(),
            GoogleMobileTranslate(),
            LingvaTranslate(),
            BaiduTranslate(),
            GoogleGtxTranslate(),
            GoogleClient5Translate(),
        ]

    def close(self):
        for backend in self._backends:
            backend.close()

    # ---------------------------------------------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------------------------------------------

    def _available_backends(self, language: LanguageCode):
        for backend in self._backends:
            if not backend.is_enabled(language):
                continue
            last_fail = self._failing.get(backend, 0)
            if time.monotonic() - last_fail < 5 * 60:
                continue
            yield backend

    def _on_backend_error(self, backend: BackendBase, e: Exception):
        message = f"{repr(backend)} failed: {':'.join(str(e).split(':')[:2])}"
        logger.info(message, exc_info=ctx.logger.is_debug)
        if "429 Client Error" in message:
            logger.warning(f"Disabling '{backend!r}' to avoid 429 error")
            self._failing[backend] = time.monotonic()

    def translate_text(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        for backend in self._available_backends(target):
            try:
                logger.info(f"Using {backend!r} for Text ({target})")
                return backend.translate(text, target, signal=signal)
            except Exception as e:
                self._on_backend_error(backend, e)
        raise ServerErrors.translation_failure.with_extra("all backends down")

    def translate_batch(
        self,
        text: Iterable[str],
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> Iterable[str]:
        for backend in self._available_backends(target):
            try:
                logger.info(f"Using {backend!r} for Batch Text ({target})")
                return backend.translate_batch(text, target, signal=signal)
            except Exception as e:
                self._on_backend_error(backend, e)
        raise ServerErrors.translation_failure.with_extra("all backends down")

    def translate_html(
        self,
        html: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> Generator[Union[int, str], None, None]:
        for backend in self._available_backends(target):
            try:
                logger.info(f"Using {backend!r} for HTML ({target})")
                return backend.translate_html(html, target, signal=signal)
            except Exception as e:
                self._on_backend_error(backend, e)
        raise ServerErrors.translation_failure.with_extra("all backends down")

    def translate_chapter(
        self,
        chapter_id: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> Generator[Tuple[int, int], None, None]:
        chapter = ctx.chapters.get(chapter_id)
        if not chapter.is_available:
            raise ServerErrors.no_such_file

        with ctx.db.session() as sess:
            row = sess.exec(
                sq.select(ChapterTranslation).where(
                    ChapterTranslation.novel_id == chapter.novel_id,
                    ChapterTranslation.chapter_serial == chapter.serial,
                    ChapterTranslation.language == target,
                )
            ).first()

        content = ctx.files.load_text(chapter.content_file)
        content_hash = sha256(content.encode()).hexdigest()
        if row and row.content_hash == content_hash and row.is_available:
            return

        total = 0
        results = []
        for out in self.translate_html(content, target, signal):
            if isinstance(out, str):
                results.append(out)
            else:
                total = out
                results.clear()
            yield len(results), total
        translated = "".join(results)

        with ctx.db.session() as sess:
            if row is None:
                row = ChapterTranslation(
                    novel_id=chapter.novel_id,
                    chapter_serial=chapter.serial,
                    language=target,
                    content_hash=content_hash,
                )
                sess.add(row)
            else:
                row.content_hash = content_hash
                sess.merge(row)
            sess.commit()

        ctx.files.save_text(row.translation_file, translated)
