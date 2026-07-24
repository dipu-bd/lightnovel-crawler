"""Novel translation on top of the embedded `lncrawl-translator` package.

Translation runs in-process: the package's `TranslatorService` (stateless,
multi-engine, glossary-aware) is owned lazily by this service, and its
dashboard is mounted into the server API. This service owns the glossary
loop: it loads a novel's stored glossary, sends it with every request, and
merges the `new_terms` the engine returns back into storage so names stay
consistent across chapters.
"""

from functools import cached_property
from hashlib import sha256
import logging
from threading import Event, Lock
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, TypeVar

import sqlmodel as sq

from ..context import ctx
from ..dao import (
    Chapter,
    ChapterTranslation,
    Novel,
    NovelGlossary,
    NovelTranslation,
    Volume,
    VolumeTranslation,
)
from ..enums import LanguageCode
from ..exceptions import AbortedException, ServerErrors

if TYPE_CHECKING:
    from translator import (
        TranslateHtmlResponse,
        TranslateTextResponse,
        TranslatorService,
    )

logger = logging.getLogger(__name__)

T = TypeVar("T")

# How many characters of the previous translated chapter to pass as continuity context.
_PREV_TAIL_CHARS = 500

# Serializes read-modify-write of a glossary row per (novel_id, language). Concurrent
# chapter/volume translation jobs of the same novel+language would otherwise both insert
# the first row (IntegrityError on the UniqueConstraint) or clobber each other's terms.
_glossary_locks: Dict[str, Lock] = {}
_glossary_locks_guard = Lock()


def _glossary_lock(novel_id: str, language: str) -> Lock:
    key = f"{novel_id}:{language}"
    with _glossary_locks_guard:
        lock = _glossary_locks.get(key)
        if lock is None:
            lock = Lock()
            _glossary_locks[key] = lock
        return lock


def _code(lang: Any) -> str:
    """The bare language code, e.g. 'en' (enum members stringify to their name otherwise)."""
    return lang.value if isinstance(lang, LanguageCode) else str(lang)


def _source_code(novel: Novel) -> Optional[str]:
    """A known source language for `novel`, or None to let the service auto-detect."""
    lang = getattr(novel, "language", None)
    if not lang:
        return None
    try:
        return LanguageCode(lang).value
    except ValueError:
        return None


class TranslationService:
    @cached_property
    def engine(self) -> "TranslatorService":
        """The embedded translator: engines, routing, and rate limits run
        in-process on the package's own event-loop thread. Its config file
        lives in the app data dir and is edited via the mounted dashboard."""
        from translator import TranslatorService

        return TranslatorService(config_path=ctx.config.translator.config_file)

    def close(self) -> None:
        if "engine" in self.__dict__:
            self.engine.close()

    # ---------------------------------------------------------------------------------------------
    # Engine plumbing
    # ---------------------------------------------------------------------------------------------

    def detect_language(self, text: str) -> Optional[str]:
        """Locally detected ISO 639-1 code for `text`, or None when unknown.
        No engine quota and no event loop involved."""
        from translator import detect_code

        return detect_code(text)

    def _invoke(self, call: Callable[[], T]) -> T:
        """Run an engine call, mapping the package's error taxonomy to ServerErrors."""
        from translator import AbortedError, ApiError, InvalidRequestError

        try:
            return call()
        except AbortedError as e:
            raise AbortedException(str(e)) from e
        except ApiError as e:
            if e.status_code == 503:
                retry = e.retry_after_seconds
                extra = f"retry after {retry}s" if retry else (e.message or "all engines busy")
                raise ServerErrors.translation_quota_exhausted.with_extra(extra) from e
            raise ServerErrors.translation_failure.with_extra(
                f"{e.status_code}: {e.message}".strip()
            ) from e
        except InvalidRequestError as e:
            raise ServerErrors.translation_failure.with_extra(e.message) from e

    # ---------------------------------------------------------------------------------------------
    # Endpoint wrappers
    # ---------------------------------------------------------------------------------------------

    def _translate_texts(
        self,
        texts: List[str],
        target: Any,
        *,
        source: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None,
        context: Optional[str] = None,
        signal: Optional[Event] = None,
    ) -> "TranslateTextResponse":
        payload: Dict[str, Any] = {
            "texts": texts,
            "target_lang": _code(target),
            "glossary": glossary or {},
        }
        if source:
            payload["source_lang"] = source
        if context:
            payload["context"] = context
        return self._invoke(
            lambda: self.engine.translate_text(
                payload,
                signal=signal,
                timeout=ctx.config.translator.request_timeout,
            )
        )

    def _translate_html(
        self,
        html: str,
        target: Any,
        *,
        source: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, str]] = None,
        extract_terms: bool = True,
        signal: Optional[Event] = None,
    ) -> "TranslateHtmlResponse":
        payload: Dict[str, Any] = {
            "html": html,
            "target_lang": _code(target),
            "glossary": glossary or {},
            "extract_terms": extract_terms,
        }
        if source:
            payload["source_lang"] = source
        if context:
            payload["context"] = context
        return self._invoke(
            lambda: self.engine.translate_html(
                payload,
                signal=signal,
                timeout=ctx.config.translator.request_timeout,
            )
        )

    # ---------------------------------------------------------------------------------------------
    # Glossary storage
    # ---------------------------------------------------------------------------------------------

    def _load_glossary(self, novel_id: str, target: Any) -> Dict[str, str]:
        with ctx.db.session() as sess:
            row = sess.exec(
                sq.select(NovelGlossary).where(
                    sq.col(NovelGlossary.novel_id) == novel_id,
                    sq.col(NovelGlossary.language) == _code(target),
                )
            ).first()
            return dict(row.terms) if row else {}

    def _merge_glossary(self, novel_id: str, target: Any, new_terms: Dict[str, str]) -> None:
        if not new_terms:
            return
        language = _code(target)
        with _glossary_lock(novel_id, language), ctx.db.session() as sess:
            row = sess.exec(
                sq.select(NovelGlossary).where(
                    sq.col(NovelGlossary.novel_id) == novel_id,
                    sq.col(NovelGlossary.language) == language,
                )
            ).first()
            if row:
                merged = dict(row.terms)
                merged.update(new_terms)
                row.terms = merged
                sess.add(row)
            else:
                sess.add(
                    NovelGlossary(
                        novel_id=novel_id,
                        language=language,
                        terms=dict(new_terms),
                    )
                )
            sess.commit()

    def _previous_chapter_tail(self, chapter: Chapter, target: Any) -> Optional[str]:
        if chapter.serial <= 1:
            return None
        with ctx.db.session() as sess:
            prev = sess.exec(
                sq.select(ChapterTranslation).where(
                    sq.col(ChapterTranslation.novel_id) == chapter.novel_id,
                    sq.col(ChapterTranslation.chapter_serial) == chapter.serial - 1,
                    sq.col(ChapterTranslation.language) == _code(target),
                )
            ).first()
        if not prev or not prev.is_available:
            return None
        from bs4 import BeautifulSoup

        text = ctx.files.load_text(prev.content_file)
        plain = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
        return plain[-_PREV_TAIL_CHARS:] if plain else None

    # ---------------------------------------------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------------------------------------------

    def translate_novel(
        self,
        novel: Novel,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> None:
        if ctx.novels.get_novel_translation(novel, target):
            return

        source = _source_code(novel)
        glossary = self._load_glossary(novel.id, target)

        result = self._translate_texts(
            [novel.title, novel.authors or ""],
            target,
            source=source,
            glossary=glossary,
            context="Web novel title and author names",
            signal=signal,
        )
        translations = result.translations
        terms = result.new_terms
        engine = result.engine
        title = translations[0] if translations else novel.title
        authors = translations[1] if len(translations) > 1 else (novel.authors or "")

        synopsis = ""
        if novel.synopsis:
            syn = self._translate_html(
                novel.synopsis,
                target,
                source=source,
                glossary={**glossary, **terms},
                context={"novel_title": title},
                signal=signal,
            )
            synopsis = syn.html
            terms = {**terms, **syn.new_terms}

        with ctx.db.session() as sess:
            sess.add(
                NovelTranslation(
                    novel_id=novel.id,
                    language=_code(target),
                    title=title,
                    authors=authors or None,
                    synopsis=synopsis or None,
                    extra={"engine": engine} if engine else {},
                )
            )
            sess.commit()

        self._merge_glossary(novel.id, target, terms)

    def translate_volume(
        self,
        volume: Volume,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> None:
        if ctx.volumes.get_volume_translation(volume, target):
            return

        glossary = self._load_glossary(volume.novel_id, target)
        result = self._translate_texts(
            [volume.title],
            target,
            glossary=glossary,
            context="Web novel volume title",
            signal=signal,
        )
        terms = result.new_terms
        engine = result.engine
        title = result.translations[0] if result.translations else volume.title

        with ctx.db.session() as sess:
            sess.add(
                VolumeTranslation(
                    novel_id=volume.novel_id,
                    volume_serial=volume.serial,
                    language=_code(target),
                    volume_title=title,
                    extra={"engine": engine} if engine else {},
                )
            )
            sess.commit()

        self._merge_glossary(volume.novel_id, target, terms)

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

        novel = ctx.novels.get(chapter.novel_id)
        source = _source_code(novel)
        glossary = self._load_glossary(chapter.novel_id, target)

        context: Dict[str, str] = {"chapter_title": chapter.title}
        if novel.title:
            context["novel_title"] = novel.title
        if novel.synopsis:
            context["synopsis"] = novel.synopsis
        tail = self._previous_chapter_tail(chapter, target)
        if tail:
            context["previous_chapter_tail"] = tail

        body = self._translate_html(
            content,
            target,
            source=source,
            glossary=glossary,
            context=context,
            signal=signal,
        )
        translated = body.html
        terms = body.new_terms
        engine = body.engine
        if body.warnings:
            logger.info(f"translate/html warnings (chapter {chapter.serial}): {body.warnings}")

        title_result = self._translate_texts(
            [chapter.title],
            target,
            source=source,
            glossary={**glossary, **terms},
            context="Web novel chapter title",
            signal=signal,
        )
        title_terms = title_result.new_terms
        title = title_result.translations[0] if title_result.translations else chapter.title

        with ctx.db.session() as sess:
            if not translation:
                translation = ChapterTranslation(
                    novel_id=chapter.novel_id,
                    chapter_serial=chapter.serial,
                    language=_code(target),
                    chapter_title=title,
                    content_hash=content_hash,
                    extra={"engine": engine} if engine else {},
                )
                sess.add(translation)
            else:
                extra = dict(**translation.extra)
                if engine:
                    extra["engine"] = engine
                sess.exec(
                    sq.update(ChapterTranslation)
                    .where(sq.col(ChapterTranslation.id) == translation.id)
                    .values(
                        chapter_title=title,
                        content_hash=content_hash,
                        extra=extra,
                    )
                )
            sess.commit()

        ctx.files.save_text(translation.content_file, translated)
        self._merge_glossary(chapter.novel_id, target, {**terms, **title_terms})
