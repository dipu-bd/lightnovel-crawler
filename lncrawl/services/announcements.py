from typing import List, Optional

import sqlmodel as sa

from ..context import ctx
from ..dao import Announcement, User
from ..exceptions import ServerErrors


class AnnouncementService:
    def list_active(self) -> List[Announcement]:
        with ctx.db.session() as sess:
            result = sess.exec(
                sa.select(Announcement)
                .where(sa.col(Announcement.is_active).is_(True))
                .order_by(sa.desc(Announcement.created_at))
            )
            return list(result)

    def list_all(
        self,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Announcement]:
        with ctx.db.session() as sess:
            result = sess.exec(
                sa.select(Announcement)
                .order_by(sa.desc(Announcement.created_at))
                .offset(offset)
                .limit(limit)
            )
            return list(result)

    def get(self, announcement_id: str) -> Announcement:
        with ctx.db.session() as sess:
            item = sess.get(Announcement, announcement_id)
            if not item:
                raise ServerErrors.not_found
            return item

    def create(
        self,
        user: User,
        *,
        title: str,
        type: str = "info",
        message: Optional[str] = None,
    ) -> Announcement:
        with ctx.db.session() as sess:
            item = Announcement(
                title=title,
                message=message,
                type=type,
                is_active=True,
                version=1,
                created_by=user.id,
            )
            sess.add(item)
            sess.commit()
            sess.refresh(item)
            return item

    def update(
        self,
        announcement_id: str,
        *,
        title: Optional[str] = None,
        message: Optional[str] = None,
        type: Optional[str] = None,
        is_active: Optional[bool] = None,
        bump_version: bool = False,
    ) -> Announcement:
        with ctx.db.session() as sess:
            item = sess.get(Announcement, announcement_id)
            if not item:
                raise ServerErrors.not_found

            if title is not None:
                item.title = title
            if message is not None:
                item.message = message
            if type is not None:
                item.type = type
            if is_active is not None:
                item.is_active = is_active
            if bump_version:
                item.version += 1

            sess.commit()
            sess.refresh(item)
            return item

    def delete(self, announcement_id: str) -> bool:
        with ctx.db.session() as sess:
            item = sess.get(Announcement, announcement_id)
            if not item:
                return True
            sess.delete(item)
            sess.commit()
            return True
