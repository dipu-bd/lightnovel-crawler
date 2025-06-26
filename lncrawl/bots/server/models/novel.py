import os
from typing import Any, Dict, List, Optional

from pydantic import computed_field, BaseModel
from sqlmodel import JSON, Column, Field, Index, func

from ._base import BaseTable
from .enums import OutputFormat


class Novel(BaseTable, table=True):
    url: str = Field(unique=True, index=True, description="The novel page url")
    orphan: Optional[bool] = Field(default=True, description='False if novel info available')

    title: Optional[str] = Field(default=None, description="The novel title")
    cover: Optional[str] = Field(default=None, description="The novel cover image", exclude=True)
    authors: Optional[str] = Field(default=None, description="The novel author")
    synopsis: Optional[str] = Field(default=None, description="The novel synopsis")
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="Tags")

    volume_count: Optional[int] = Field(default=None, description="Volume count")
    chapter_count: Optional[int] = Field(default=None, description="Chapter count")

    extra: Dict[str, Any] = Field(default={}, sa_column=Column(JSON), description="Extra field")

    __table_args__ = (
        Index("idx_novel_title_lower", func.lower(title)),
    )


class Artifact(BaseTable, table=True):
    novel_id: str = Field(foreign_key="novel.id", ondelete='CASCADE')
    job_id: Optional[str] = Field(foreign_key="job.id", ondelete='SET NULL')

    output_file: str = Field(description="Output file path", exclude=True)
    format: OutputFormat = Field(index=True, description="The output format of the artifact")

    extra: Dict[str, Any] = Field(default={}, sa_column=Column(JSON), description="Extra field")

    @computed_field  # type:ignore
    @property
    def file_name(self) -> str:
        '''Output file name'''
        return os.path.basename(self.output_file)

    @computed_field  # type:ignore
    @property
    def is_available(self) -> bool:
        '''Output file is available'''
        return os.path.isfile(self.output_file)

    @computed_field  # type:ignore
    @property
    def file_size(self) -> Optional[int]:
        '''Output file size in bytes'''
        try:
            stat = os.stat(self.output_file)
            return stat.st_size
        except Exception:
            return None


class NovelChapter(BaseModel):
    id: int
    title: str
    hash: str


class NovelVolume(BaseModel):
    id: int
    title: str
    chapters: List[NovelChapter] = []


class NovelChapterContent(BaseModel):
    id: int
    title: str
    body: str
    volume_id: int
    volume: str
    prev: Optional[NovelChapter] = None
    next: Optional[NovelChapter] = None
