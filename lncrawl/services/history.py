from typing import Dict, Optional

from sqlalchemy import delete as sa_delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, desc, select

from ..context import ctx
from ..core.taskman import TaskManager
from ..dao import ReadHistory


class ReadHistoryService:
    def __init__(self) -> None:
        self.taskman = TaskManager(5)

    def list(
        self,
        user_id: str,
        *,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
    ) -> Dict[str, bool]:
        with ctx.db.session() as sess:
            stmt = select(ReadHistory)
            stmt = stmt.where(ReadHistory.user_id == user_id)

            if novel_id:
                ids = [x.strip() for x in novel_id.split(",")]
                stmt = stmt.where(col(ReadHistory.novel_id).in_(ids))
            if volume_id:
                ids = [x.strip() for x in volume_id.split(",")]
                stmt = stmt.where(col(ReadHistory.volume_id).in_(ids))
            if chapter_id:
                ids = [x.strip() for x in chapter_id.split(",")]
                stmt = stmt.where(col(ReadHistory.chapter_id).in_(ids))

            items = sess.exec(stmt).all()
            return {item.chapter_id: True for item in items}

    def check(self, user_id: str, chapter_id: str) -> bool:
        with ctx.db.session() as sess:
            item = sess.exec(
                select(ReadHistory.id)
                .where(ReadHistory.user_id == user_id)
                .where(ReadHistory.chapter_id == chapter_id)
            ).first()
            return bool(item)

    def add(self, user_id: str, chapter_id: str) -> None:
        with ctx.db.session() as sess:
            chapter = ctx.chapters.get(chapter_id)
            try:
                history = ReadHistory(
                    user_id=user_id,
                    chapter_id=chapter_id,
                    novel_id=chapter.novel_id,
                    volume_id=chapter.volume_id,
                )
                sess.add(history)
                sess.commit()
                self.taskman.submit_task(self.prune, user_id)
            except IntegrityError:
                sess.rollback()
                return

    def prune(self, user_id: str) -> None:
        with ctx.db.session() as sess:
            tbd = (
                select(ReadHistory.id)
                .where(ReadHistory.user_id == user_id)
                .order_by(desc(ReadHistory.created_at))
                .offset(ctx.config.app.history_limit_per_user)
                .scalar_subquery()
            )
            stmt = sa_delete(ReadHistory).where(col(ReadHistory.id).in_(tbd))
            sess.exec(stmt)
            sess.commit()
