from typing import List, Optional

import sqlmodel as sa
from pydantic import computed_field

from ..context import ctx
from ._base import BaseTable


class Novel(BaseTable, table=True):
    __tablename__ = "novels"  # type: ignore

    domain: str = sa.Field(index=True, description="Domain name of the source website")
    url: str = sa.Field(unique=True, description="Full URL of the novel main page")

    title: str = sa.Field(description="Title of the novel")
    authors: Optional[str] = sa.Field(default=None, description="Comma-separated list of authors")
    synopsis: Optional[str] = sa.Field(
        default=None, description="Brief synopsis or novel description"
    )
    tags: List[str] = sa.Field(
        default=[], sa_type=sa.JSON, description="List of genre or thematic tags"
    )
    cover_url: Optional[str] = sa.Field(
        default=None,
        description="Cover image URL",
    )

    mtl: bool = sa.Field(default=False, description="True if content is machine-translated")
    rtl: bool = sa.Field(
        default=False, description="True if text reads right-to-left (e.g. Arabic, Hebrew)"
    )
    manga: bool = sa.Field(default=False, description="True if this entry is a manga/manhua/comic")
    language: Optional[str] = sa.Field(
        default=None,
        sa_column=sa.Column(sa.CHAR(2)),
        description="ISO 639-1 two-letter language code (e.g. 'en', 'ja', 'zh')",
    )

    volume_count: int = sa.Field(
        default=0,
        description="Number of available volumes",
    )
    chapter_count: int = sa.Field(
        default=0,
        description="Number of available chapters",
    )

    @computed_field  # type: ignore[misc]
    @property
    def cover_file(self) -> str:
        """Cover image file path"""
        return f"novels/{self.id}/cover.jpg"

    @computed_field  # type: ignore[misc]
    @property
    def cover_available(self) -> bool:
        """Whether the cover image file is available"""
        return ctx.files.exists(self.cover_file)
