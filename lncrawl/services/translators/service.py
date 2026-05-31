from hashlib import sha256
import logging
from threading import Event
import time
from typing import Dict, Generator, Iterable, List, Optional, Union

import sqlmodel as sq

from ...context import ctx
from ...dao import Chapter, ChapterTranslation, Novel, NovelTranslation, Volume, VolumeTranslation
from ...enums import LanguageCode
from ...exceptions import ServerErrors
from .backend_baidu import BaiduTranslate
from .backend_base import BackendBase
from .backend_bing import BingTranslate
from .backend_google import GoogleClient5Translate, GoogleGtxTranslate, GoogleMobileTranslate
from .backend_lingva import LingvaTranslate

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
            logger.warning(f"Disabling '{backend.name}' to avoid 429 error")
            self._failing[backend] = time.monotonic()

    def translate_text(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        for backend in self._available_backends(target):
            try:
                logger.info(f"Using {backend.name} for Text ({target})")
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
                logger.info(f"Using {backend.name} for Batch Text ({target})")
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
                logger.info(f"Using {backend.name} for HTML ({target})")
                return backend.translate_html(html, target, signal=signal)
            except Exception as e:
                self._on_backend_error(backend, e)
        raise ServerErrors.translation_failure.with_extra("all backends down")

    def translate_novel(
        self,
        novel: Novel,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> None:
        translation = ctx.novels.get_novel_translation(novel, target)
        if translation:
            return

        texts = [
            novel.title,
            novel.authors or "",
        ]
        (title, authors) = self.translate_batch(texts, target, signal)

        synopsis: List[str] = []
        if novel.synopsis:
            for out in self.translate_html(novel.synopsis, target, signal):
                if isinstance(out, str):
                    synopsis.append(out)

        with ctx.db.session() as sess:
            translation = NovelTranslation(
                novel_id=novel.id,
                language=target,
                title=title,
                authors=authors,
                synopsis="".join(synopsis),
            )
            sess.add(translation)
            sess.commit()

    def translate_volume(
        self,
        volume: Volume,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> None:
        translation = ctx.volumes.get_volume_translation(volume, target)
        if translation:
            return

        title = self.translate_text(volume.title, target, signal)
        with ctx.db.session() as sess:
            translation = VolumeTranslation(
                novel_id=volume.novel_id,
                volume_serial=volume.serial,
                language=target,
                volume_title=title,
            )
            sess.add(translation)
            sess.commit()

    def translate_chapter(
        self,
        chapter: Chapter,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> None:
        translation = ctx.chapters.get_chapter_translation(chapter, target)

        content = ctx.files.load_text(chapter.content_file)
        content_hash = sha256(content.encode()).hexdigest()
        if translation and translation.content_hash == content_hash and translation.is_available:
            return

        results = []
        for out in self.translate_html(content, target, signal):
            if isinstance(out, str):
                results.append(out)
        translated = "".join(results)

        title = self.translate_text(chapter.title, target)

        with ctx.db.session() as sess:
            if not translation:
                translation = ChapterTranslation(
                    novel_id=chapter.novel_id,
                    chapter_serial=chapter.serial,
                    language=target,
                    chapter_title=title,
                    content_hash=content_hash,
                )
                sess.add(translation)
            else:
                sess.exec(
                    sq.update(ChapterTranslation)
                    .where(sq.col(ChapterTranslation.id) == translation.id)
                    .values(
                        chapter_title=title,
                        content_hash=content_hash,
                    )
                )
            sess.commit()

        ctx.files.save_text(translation.content_file, translated)
