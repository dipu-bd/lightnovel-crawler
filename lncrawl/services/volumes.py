from typing import List, Optional

import sqlmodel as sq

from ..context import ctx
from ..core import Volume as CrawlerVolume
from ..dao import LanguageCode, User, UserRole, Volume, VolumeTranslation
from ..exceptions import ServerErrors


class VolumeService:
    def __init__(self) -> None:
        pass

    def count(self, novel_id: str) -> int:
        with ctx.db.session() as sess:
            stmt = sq.select(sq.func.count()).select_from(Volume)
            stmt = stmt.where(Volume.novel_id == novel_id)
            return sess.exec(stmt).one()

    def list(self, novel_id: str, language: Optional[LanguageCode] = None) -> List[Volume]:
        with ctx.db.session() as sess:
            stmt = sq.select(Volume)
            stmt = stmt.where(Volume.novel_id == novel_id)
            stmt = stmt.order_by(sq.col(Volume.serial).asc())
            items = list(sess.exec(stmt).all())
        self._put_translations(items, language)
        return items

    def _put_translations(
        self,
        items: List[Volume],
        language: Optional[LanguageCode],
    ):
        if language and items:
            novel_id = items[0].novel_id
            with ctx.db.session() as sess:
                translations = sess.exec(
                    sq.select(VolumeTranslation).where(
                        VolumeTranslation.novel_id == novel_id,
                        VolumeTranslation.language == language,
                    )
                ).all()
                serial_title_map = {t.volume_serial: t.volume_title for t in translations}
            for item in items:
                item.title = serial_title_map.get(item.serial) or item.title

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

    def get_volume_translation(self, volume: Volume, language: LanguageCode):
        with ctx.db.session() as sess:
            return sess.exec(
                sq.select(VolumeTranslation)
                .where(
                    VolumeTranslation.novel_id == volume.novel_id,
                    VolumeTranslation.volume_serial == volume.serial,
                    VolumeTranslation.language == language,
                )
                .limit(1)
            ).first()

    def get_translated(self, volume_id: str, language: Optional[LanguageCode] = None) -> Volume:
        volume = self.get(volume_id)
        if language:
            translation = self.get_volume_translation(volume, language)
            if not translation:
                raise ServerErrors.no_such_volume.with_extra(language)
            volume.title = translation.volume_title
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
                            extra=wanted[s].get_extras(),
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
                            extra=wanted[s].get_extras(),
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
