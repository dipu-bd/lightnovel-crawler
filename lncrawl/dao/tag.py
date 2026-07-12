from typing import Optional

import sqlmodel as sa


class Tag(sa.SQLModel, table=True):
    __tablename__ = "tags"  # type: ignore

    name: str = sa.Field(nullable=False, primary_key=True, description="Unique tag name")
    description: Optional[str] = sa.Field(default=None, description="Tag description")


class NovelTag(sa.SQLModel, table=True):
    __tablename__ = "novel_tags"  # type: ignore
    __table_args__ = (sa.Index("ix_novel_tag_name", "tag_name"),)

    novel_id: str = sa.Field(foreign_key="novels.id", ondelete="CASCADE", primary_key=True)
    tag_name: str = sa.Field(primary_key=True, description="Tag name")
