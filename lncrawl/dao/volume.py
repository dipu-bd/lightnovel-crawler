import sqlmodel as sa

from ._base import BaseTable


class Volume(BaseTable, table=True):
    __tablename__ = "volumes"  # type: ignore
    __table_args__ = (
        sa.UniqueConstraint("novel_id", "serial"),
        sa.Index("ix_volume_novel_id", "novel_id"),
        sa.Index("ix_volume_novel_serial", "novel_id", "serial"),
    )

    novel_id: str = sa.Field(
        foreign_key="novels.id",
        ondelete="CASCADE",
    )
    serial: int = sa.Field(
        description="Serial number of the volume",
    )
    title: str = sa.Field(
        description="Name of the volume",
    )
    chapter_count: int = sa.Field(
        default=0,
        description="Number of available chapters",
    )


class VolumeTranslation(BaseTable, table=True):
    __tablename__ = "volume_translations"  # type: ignore
    __table_args__ = (
        sa.UniqueConstraint("novel_id", "volume_serial", "language"),
        sa.Index("ix_volume_translation_lookup", "novel_id", "volume_serial", "language"),
    )

    novel_id: str = sa.Field(foreign_key="novels.id", ondelete="CASCADE")
    volume_serial: int = sa.Field(description="volume serial number within the novel")
    language: str = sa.Field(description="Target language code, e.g. 'fr'")
    volume_title: str = sa.Field(description="Translated title of the volume")
