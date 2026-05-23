from typing import Any, Dict, List, Optional

import sqlmodel as sq

from ..context import ctx
from ..core import Chapter as CrawlerChapter, PageSoup
from ..dao import Chapter, Job, User, UserTier, Volume
from ..dao.chapter import ChapterTranslation
from ..exceptions import ServerErrors
from ..server.models import Paginated, ReadChapterResponse


class ChapterService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        *,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
        is_crawled: Optional[bool] = None,
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
            items = sess.exec(stmt).all()
            return list(items)

    def list_page(
        self,
        offset: int = 0,
        limit: int = 20,
        *,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
        is_crawled: Optional[bool] = None,
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
            items = sess.exec(stmt).all()

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

    def get_chapter_translation(self, chapter: Chapter, language: str):
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

    def read(
        self,
        user: User,
        chapter_id: str,
        language: Optional[str] = None,
        auto_fetch: Optional[bool] = None,
    ) -> ReadChapterResponse:
        chapter = self.get(chapter_id)
        novel = ctx.novels.get(chapter.novel_id)
        if auto_fetch is None:
            auto_fetch = user.tier != UserTier.BASIC

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

        ctx.history.add(user.id, chapter.id)

        job: Optional[Job] = None
        content: Optional[str] = None
        word_count: Optional[int] = None
        if chapter.is_available:
            if language:
                translation = self.get_chapter_translation(chapter, language)
                if translation and translation.is_available:
                    content = ctx.files.load_text(translation.translation_file)
                elif auto_fetch:
                    job = ctx.jobs.get_translation_job(user.id, chapter_id, language)
                    if not job:
                        job = ctx.jobs.translate_chapter(user, chapter_id, language)
            else:
                content = ctx.files.load_text(chapter.content_file)
        elif auto_fetch:
            job = ctx.jobs.get_chapter_job(user.id, chapter_id)
            if not job:
                job = ctx.jobs.fetch_chapter(user, chapter_id)

        if content:
            word_count = PageSoup.create(content).word_count()

        return ReadChapterResponse(
            job=job,
            novel=novel,
            chapter=chapter,
            content=content,
            language=language,
            word_count=word_count,
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
