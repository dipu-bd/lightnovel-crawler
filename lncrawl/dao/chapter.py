from typing import Optional

from pydantic import computed_field
import sqlmodel as sa

from ..context import ctx
from ._base import BaseTable


class Chapter(BaseTable, table=True):
    __tablename__ = "chapters"  # type: ignore
    __table_args__ = (
        sa.UniqueConstraint("novel_id", "serial"),
        sa.Index("ix_chapter_novel_id", "novel_id"),
        sa.Index("ix_chapter_novel_serial", "novel_id", "serial"),
        sa.Index("ix_chapter_novel_volume", "novel_id", "volume_id"),
    )

    novel_id: str = sa.Field(foreign_key="novels.id", ondelete="CASCADE")
    serial: int = sa.Field(
        description="Serial number of the chapter",
    )
    volume_id: Optional[str] = sa.Field(
        default=None,
        foreign_key="volumes.id",
        ondelete="SET NULL",
        nullable=True,
    )

    url: str = sa.Field(description="Full URL of the chapter content page")
    title: str = sa.Field(description="Title of the chapter")
    is_done: bool = sa.Field(default=False, description="Whether the content has been crawled")

    @computed_field  # type: ignore[misc]
    @property
    def content_file(self) -> str:
        """Content file path"""
        return f"novels/{self.novel_id}/chapters/{self.serial:06}.zst"

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        """Content file is available"""
        return ctx.files.exists(self.content_file)


class ChapterTranslation(BaseTable, table=True):
    __tablename__ = "chapter_translations"  # type: ignore
    __table_args__ = (
        sa.UniqueConstraint("novel_id", "chapter_serial", "language"),
        sa.Index("ix_chapter_translation_lookup", "novel_id", "chapter_serial", "language"),
    )

    novel_id: str = sa.Field(foreign_key="novels.id", ondelete="CASCADE")
    chapter_serial: int = sa.Field(description="Chapter serial number within the novel")
    language: str = sa.Field(description="Target language code, e.g. 'fr'")
    chapter_title: str = sa.Field(description="Translated title of the chapter")
    content_hash: str = sa.Field(description="SHA256 of original content for cache invalidation")

    @computed_field  # type: ignore[misc]
    @property
    def content_file(self) -> str:
        """Translation content file path"""
        return f"novels/{self.novel_id}/chapters/{self.chapter_serial:06}.{self.language}.zst"

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        """Translation content file is available"""
        return ctx.files.exists(self.content_file)
