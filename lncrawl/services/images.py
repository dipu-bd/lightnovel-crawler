from typing import Dict, List, Optional

import sqlmodel as sq

from ..context import ctx
from ..dao import Chapter, ChapterImage
from ..exceptions import ServerErrors


class ChapterImageService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        novel_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        is_crawled: Optional[bool] = None,
    ) -> List[ChapterImage]:
        with ctx.db.session() as sess:
            stmt = sq.select(ChapterImage)
            if novel_id:
                stmt = stmt.where(ChapterImage.novel_id == novel_id)
            if chapter_id:
                stmt = stmt.where(ChapterImage.chapter_id == chapter_id)
            if is_crawled:
                stmt = stmt.where(sq.col(ChapterImage.is_done).is_(True))
            items = sess.exec(stmt).all()
            return list(items)

    def list_ids(
        self,
        novel_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
    ) -> List[str]:
        with ctx.db.session() as sess:
            stmt = sq.select(ChapterImage.id)
            if novel_id:
                stmt = stmt.where(ChapterImage.novel_id == novel_id)
            if chapter_id:
                stmt = stmt.where(ChapterImage.chapter_id == chapter_id)
            items = sess.exec(stmt).all()
            return list(items)

    def get(self, image_id: str) -> ChapterImage:
        with ctx.db.session() as sess:
            image = sess.get(ChapterImage, image_id)
            if not image:
                raise ServerErrors.no_such_file
            return image

    def get_many(self, image_ids: List[str]) -> List[ChapterImage]:
        with ctx.db.session() as sess:
            stmt = sq.select(ChapterImage).where(sq.col(ChapterImage.id).in_(image_ids))
            items = sess.exec(stmt).all()
            return list(items)

    def delete(self, image_id: str) -> bool:
        with ctx.db.session() as sess:
            image = sess.get(ChapterImage, image_id)
            if not image:
                return True
            ctx.files.resolve(image.image_file).unlink(True)
            sess.delete(image)
            sess.commit()
            return True

    def sync(self, chapter: Chapter, images: Dict[str, str]):
        with ctx.db.session() as sess:
            existing = {
                img.id: img
                for img in sess.exec(
                    sq.select(ChapterImage).where(ChapterImage.chapter_id == chapter.id)
                ).all()
            }

            wk = set(images.keys())
            ek = set(existing.keys())
            to_insert = wk - ek
            to_delete = ek - wk

            if to_insert:
                crawler_version = chapter.extra.get("crawler_version")
                sess.exec(
                    sq.insert(ChapterImage),
                    params=[
                        ChapterImage(
                            id=id,
                            url=images[id],
                            chapter_id=chapter.id,
                            novel_id=chapter.novel_id,
                            extra=dict(crawler_version=crawler_version),
                        ).model_dump()
                        for id in to_insert
                    ],
                )

            if to_delete:
                sess.exec(sq.delete(ChapterImage).where(sq.col(ChapterImage.id).in_(to_delete)))
                for id in to_delete:
                    file = existing[id].image_file
                    ctx.files.resolve(file).unlink(True)

            sess.commit()
