from typing import List

import sqlmodel as sq

from ..context import ctx
from ..core import Volume as CrawlerVolume
from ..core.models import get_extras
from ..dao import User, UserRole, Volume
from ..exceptions import ServerErrors


class VolumeService:
    def __init__(self) -> None:
        pass

    def count(self, novel_id: str) -> int:
        with ctx.db.session() as sess:
            stmt = sq.select(sq.func.count()).select_from(Volume)
            stmt = stmt.where(Volume.novel_id == novel_id)
            return sess.exec(stmt).one()

    def list(self, novel_id: str) -> List[Volume]:
        with ctx.db.session() as sess:
            stmt = sq.select(Volume)
            stmt = stmt.where(Volume.novel_id == novel_id)
            stmt = stmt.order_by(sq.col(Volume.serial).asc())
            items = sess.exec(stmt).all()
            return list(items)

    def get(self, volume_id: str) -> Volume:
        with ctx.db.session() as sess:
            volume = sess.get(Volume, volume_id)
            if not volume:
                raise ServerErrors.no_such_volume
            return volume

    def get_many(self, volume_ids: List[str]) -> List[Volume]:
        with ctx.db.session() as sess:
            stmt = sq.select(Volume).where(sq.col(Volume.id).in_(volume_ids))
            items = sess.exec(stmt).all()
            return list(items)

    def delete(self, volume_id: str, user: User) -> bool:
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
        with ctx.db.session() as sess:
            volume = sess.get(Volume, volume_id)
            if not volume:
                return True
            sess.delete(volume)
            sess.commit()
            return True

    def find(self, novel_id: str, serial: int) -> Volume:
        with ctx.db.session() as sess:
            stmt = sq.select(Volume).where(
                Volume.novel_id == novel_id,
                Volume.serial == serial,
            )
            volume = sess.exec(stmt).first()
            if not volume:
                raise ServerErrors.no_such_volume
            return volume

    def sync(self, novel_id: str, volumes: List[CrawlerVolume]):
        with ctx.db.session() as sess:
            wanted = {v.id: v for v in volumes}
            existing = {
                v.serial: v
                for v in sess.exec(sq.select(Volume).where(Volume.novel_id == novel_id)).all()
            }

            wk = set(wanted.keys())
            ek = set(existing.keys())
            to_insert = wk - ek
            to_delete = ek - wk
            to_update = ek & wk

            if to_insert:
                sess.exec(
                    sq.insert(Volume),
                    params=[
                        Volume(
                            serial=s,
                            novel_id=novel_id,
                            title=wanted[s].title,
                            extra=get_extras(wanted[s]),
                            chapter_count=wanted[s].chapters,
                        ).model_dump()
                        for s in to_insert
                    ],
                )

            if to_update:
                sess.exec(
                    sq.update(Volume),
                    params=[
                        Volume(
                            id=existing[s].id,
                            serial=s,
                            novel_id=novel_id,
                            title=wanted[s].title,
                            extra=get_extras(wanted[s]),
                            chapter_count=wanted[s].chapters,
                        ).model_dump()
                        for s in to_update
                    ],
                )

            if to_delete:
                sess.exec(
                    sq.delete(Volume)
                    .where(sq.col(Volume.novel_id) == novel_id)
                    .where(sq.col(Volume.serial).in_(to_delete))
                )

            sess.commit()
