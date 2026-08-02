from itertools import islice
from typing import Any, Dict, Iterable, List, NamedTuple, Optional

from sqlalchemy.dialects.postgresql import JSONB
import sqlmodel as sq

from ..context import ctx
from ..core import Chapter as CrawlerChapter, PageSoup
from ..dao import Chapter, Job, LanguageCode, User, Volume
from ..dao.chapter import ChapterTranslation
from ..exceptions import ServerErrors
from ..server.models import Paginated, ReadChapterResponse

# An empty body still compresses to a frame of a few bytes, so size cannot decide
# emptiness on its own — but it rules a file out without opening it, which is what keeps
# a sweep across every finished chapter in the library cheap.
EMPTY_CANDIDATE_BYTES = 512

# SQLite binds each member of an IN clause as its own variable, and older builds stop at
# 999 of them.
_ID_CHUNK = 500

# Rows pulled per round trip when streaming a scan over the whole chapter table.
_SCAN_CHUNK = 1000

# The `extra` key counting how many times a chapter came back with no text. Named here
# because both the download path that writes it and the query that clears it have to agree,
# and they did not: the clear was built from the column object rather than the key.
EMPTY_ATTEMPTS_KEY = "empty_attempts"


class EmptyChapter(NamedTuple):
    id: str
    novel_id: str
    serial: int


class ChapterService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        *,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
        is_crawled: Optional[bool] = None,
        language: Optional[LanguageCode] = None,
    ) -> List[Chapter]:
        with ctx.db.session() as sess:
            stmt = sq.select(Chapter)
            if novel_id:
                stmt = stmt.where(Chapter.novel_id == novel_id)
            if volume_id:
                stmt = stmt.where(Chapter.volume_id == volume_id)
            if is_crawled is not None:
                stmt = stmt.where(sq.col(Chapter.is_done).is_(is_crawled))
            stmt = stmt.order_by(sq.col(Chapter.serial).asc())
            items = list(sess.exec(stmt).all())
        self._put_translations(items, language)
        return items

    def list_page(
        self,
        offset: int = 0,
        limit: int = 20,
        *,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
        is_crawled: Optional[bool] = None,
        language: Optional[LanguageCode] = None,
    ) -> Paginated[Chapter]:
        with ctx.db.session() as sess:
            stmt = sq.select(Chapter)
            cnt = sq.select(sq.func.count()).select_from(Chapter)

            # Apply filters
            conditions: List[Any] = []
            if novel_id:
                conditions += [Chapter.novel_id == novel_id]
            if volume_id:
                conditions += [Chapter.volume_id == volume_id]
            if is_crawled is not None:
                conditions += [sq.col(Chapter.is_done).is_(is_crawled)]

            if conditions:
                cnt = cnt.where(*conditions)
                stmt = stmt.where(*conditions)

            # Apply sorting
            stmt = stmt.order_by(sq.col(Chapter.serial).asc())

            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)

            total = sess.exec(cnt).one()
            items = list(sess.exec(stmt).all())

            # get translations
            self._put_translations(items, language)

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def list_ids(
        self,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
        is_crawled: Optional[bool] = None,
        descending: bool = False,
        limit: Optional[int] = None,
    ) -> List[str]:
        with ctx.db.session() as sess:
            stmt = sq.select(Chapter.id)
            if novel_id:
                stmt = stmt.where(Chapter.novel_id == novel_id)
            if volume_id:
                stmt = stmt.where(Chapter.volume_id == volume_id)
            if is_crawled is not None:
                stmt = stmt.where(sq.col(Chapter.is_done).is_(is_crawled))
            if descending:
                stmt = stmt.order_by(sq.col(Chapter.serial).desc())
            else:
                stmt = stmt.order_by(sq.col(Chapter.serial).asc())
            if limit:
                stmt = stmt.limit(limit)
            items = sess.exec(stmt).all()
            return list(items)

    def find(self, novel_id: str, serial: int) -> Chapter:
        with ctx.db.session() as sess:
            stmt = sq.select(Chapter).where(
                Chapter.novel_id == novel_id,
                Chapter.serial == serial,
            )
            chapter = sess.exec(stmt).first()
            if not chapter:
                raise ServerErrors.no_such_chapter
            return chapter

    def get(self, chapter_id: str) -> Chapter:
        with ctx.db.session() as sess:
            chapter = sess.get(Chapter, chapter_id)
            if not chapter:
                raise ServerErrors.no_such_chapter
            return chapter

    def get_many(self, chapter_ids: List[str]) -> List[Chapter]:
        with ctx.db.session() as sess:
            items = sess.exec(sq.select(Chapter).where(sq.col(Chapter.id).in_(chapter_ids))).all()
            return list(items)

    def delete(self, chapter_id: str) -> None:
        with ctx.db.session() as sess:
            chapter = sess.get(Chapter, chapter_id)
            if not chapter:
                return
            ctx.files.resolve(chapter.content_file).unlink(True)
            sess.delete(chapter)
            sess.commit()

    def find_stored_empty(self, *, untried_only: bool = False) -> Iterable[EmptyChapter]:
        """Find chapters marked finished over stored content that holds no text."""
        stmt = sq.select(
            Chapter.id,
            Chapter.novel_id,
            Chapter.serial,
        ).where(
            sq.col(Chapter.is_done).is_(True),
        )
        if untried_only:
            stmt = stmt.where(
                Chapter.extra[EMPTY_ATTEMPTS_KEY].as_string().is_(None),
            )

        with ctx.db.session() as sess:
            rows = sess.exec(stmt.execution_options(yield_per=_SCAN_CHUNK))
            for chapter_id, novel_id, serial in rows:
                if self._is_stored_empty(novel_id, serial):
                    yield EmptyChapter(chapter_id, novel_id, serial)

    def reopen_empty(self, chapter_ids: Iterable[str], *, reset_attempts: bool = False) -> int:
        """Clear `is_done` so these chapters are downloaded again."""
        sa_extra = Chapter.extra
        if reset_attempts:
            extra_col = sq.col(Chapter.extra)
            if ctx.db.engine.dialect.name == "postgresql":
                empty_literal = sq.literal(EMPTY_ATTEMPTS_KEY)
                replaced_json = sq.cast(extra_col, JSONB).op("-")(empty_literal)
                sa_extra = sq.cast(replaced_json, sq.JSON)
            else:
                sa_extra = sq.func.json_remove(extra_col, f'$."{EMPTY_ATTEMPTS_KEY}"')

        total = 0
        with ctx.db.session() as sess:
            iterator = iter(chapter_ids)
            while batch := list(islice(iterator, _ID_CHUNK)):
                result = sess.exec(
                    sq.update(Chapter)
                    .where(sq.col(Chapter.id).in_(batch))
                    .values(is_done=False, extra=sa_extra)
                )
                total += result.rowcount or 0
            sess.commit()
        return total

    @staticmethod
    def _is_stored_empty(novel_id: str, serial: int) -> bool:
        content_file = Chapter.content_path(novel_id, serial)
        try:
            path = ctx.files.resolve(content_file)
        except Exception:
            return False
        if not path.exists():
            return True
        try:
            if path.stat().st_size > EMPTY_CANDIDATE_BYTES:
                return False
            return not ctx.files.load_text(content_file).strip()
        except Exception:
            return False

    @staticmethod
    def _put_translations(items: List[Chapter], language: Optional[LanguageCode]) -> None:
        if language and items:
            novel_id = items[0].novel_id
            serials = [item.serial for item in items]
            with ctx.db.session() as sess:
                translations = sess.exec(
                    sq.select(ChapterTranslation).where(
                        ChapterTranslation.novel_id == novel_id,
                        ChapterTranslation.language == language,
                        sq.col(ChapterTranslation.chapter_serial).in_(serials),
                    )
                ).all()
                serial_title_map = {t.chapter_serial: t.chapter_title for t in translations}
            for item in items:
                item.title = serial_title_map.get(item.serial) or item.title

    def get_chapter_translation(self, chapter: Chapter, language: LanguageCode):
        with ctx.db.session() as sess:
            return sess.exec(
                sq.select(ChapterTranslation)
                .where(
                    ChapterTranslation.novel_id == chapter.novel_id,
                    ChapterTranslation.chapter_serial == chapter.serial,
                    ChapterTranslation.language == language,
                )
                .limit(1)
            ).first()

    def get_translated(
        self,
        chapter_id: str,
        language: Optional[LanguageCode] = None,
    ) -> Chapter:
        chapter = self.get(chapter_id)
        if language:
            translation = self.get_chapter_translation(chapter, language)
            if not translation:
                raise ServerErrors.no_such_chapter.with_extra(language)
            chapter.title = translation.chapter_title
        return chapter

    def read(
        self,
        user: User,
        chapter_id: str,
        *,
        auto_fetch: Optional[bool] = None,
        language: Optional[LanguageCode] = None,
    ) -> ReadChapterResponse:
        if auto_fetch is None:
            auto_fetch = ctx.tier.auto_fetch_enabled(user)

        chapter = self.get(chapter_id)

        job: Optional[Job] = None
        content: Optional[str] = None
        if chapter.is_available:
            content = ctx.files.load_text(chapter.content_file)
        elif auto_fetch:
            job = ctx.jobs.get_chapter_job(user.id, chapter_id)
            if not job:
                job = ctx.jobs.fetch_chapter(user, chapter_id)

        translation_engine: Optional[str] = None
        if language:
            content = None
            chapter_translation = self.get_chapter_translation(chapter, language)
            if chapter_translation and chapter_translation.is_available:
                chapter.title = chapter_translation.chapter_title or chapter.title
                content = ctx.files.load_text(chapter_translation.content_file)
                translation_engine = chapter_translation.extra.get("engine")
            elif not ctx.config.translator.enabled:
                raise ServerErrors.translation_disabled
            elif not ctx.tier.translation_enabled(user):
                raise ServerErrors.tier_not_allowed
            elif auto_fetch:
                fetch_job_id = job.id if job else None
                translate_job = ctx.jobs.get_chapter_translation_job(user.id, chapter_id, language)
                if not translate_job:
                    translate_job = ctx.jobs.translate_chapter(
                        user, chapter_id, language, depends_on=fetch_job_id
                    )
                if not job or job.is_done:
                    job = translate_job

        word_count: Optional[int] = None
        if content:
            word_count = PageSoup.create(content).word_count()

        novel = ctx.novels.get(chapter.novel_id, language)
        with ctx.db.session() as sess:
            previous_id = sess.exec(
                sq.select(Chapter.id)
                .where(Chapter.novel_id == novel.id)
                .where(Chapter.serial == (chapter.serial - 1))
                .limit(1)
            ).first()
            next_id = sess.exec(
                sq.select(Chapter.id)
                .where(Chapter.novel_id == novel.id)
                .where(Chapter.serial == (chapter.serial + 1))
                .limit(1)
            ).first()

        return ReadChapterResponse(
            job=job,
            novel=novel,
            chapter=chapter,
            content=content,
            language=language,
            word_count=word_count,
            translation_engine=translation_engine,
            next_id=next_id,
            previous_id=previous_id,
        )

    def sync(self, novel_id: str, chapters: List[CrawlerChapter]):
        with ctx.db.session() as sess:
            vol_id_map: Dict[Optional[int], str] = {
                v.serial: v.id
                for v in sess.exec(sq.select(Volume).where(Volume.novel_id == novel_id)).all()
            }

            wanted = {c.id: c for c in chapters}
            existing = {
                c.serial: c
                for c in sess.exec(sq.select(Chapter).where(Chapter.novel_id == novel_id)).all()
            }

            wk = set(wanted.keys())
            ek = set(existing.keys())
            to_insert = wk - ek
            to_delete = ek - wk
            to_update = ek & wk

            if to_insert:
                sess.exec(
                    sq.insert(Chapter),
                    params=[
                        Chapter(
                            serial=s,
                            novel_id=novel_id,
                            url=wanted[s].url,
                            title=wanted[s].title,
                            extra=wanted[s].get_extras(),
                            volume_id=vol_id_map.get(wanted[s].volume),
                        ).model_dump()
                        for s in to_insert
                    ],
                )

            if to_update:
                sess.exec(
                    sq.update(Chapter),
                    params=[
                        Chapter(
                            id=existing[s].id,
                            serial=s,
                            novel_id=novel_id,
                            url=wanted[s].url,
                            title=wanted[s].title,
                            is_done=existing[s].is_done,
                            extra={**existing[s].extra, **wanted[s].get_extras()},
                            volume_id=vol_id_map.get(wanted[s].volume),
                        ).model_dump()
                        for s in to_update
                    ],
                )

            if to_delete:
                sess.exec(
                    sq.delete(Chapter)
                    .where(sq.col(Chapter.novel_id) == novel_id)
                    .where(sq.col(Chapter.serial).in_(to_delete))
                )
                for serial in to_delete:
                    file = existing[serial].content_file
                    ctx.files.resolve(file).unlink(True)

            sess.commit()
