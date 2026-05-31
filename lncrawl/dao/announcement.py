from typing import Optional

import sqlmodel as sa

from ._base import BaseTable


class Announcement(BaseTable, table=True):
    __tablename__ = "announcements"  # type: ignore
    __table_args__ = (
        sa.Index("ix_announcement_is_active", "is_active"),
        sa.Index("ix_announcement_version", "version"),
    )

    title: str = sa.Field(
        description="Announcement title",
    )
    message: Optional[str] = sa.Field(
        nullable=True,
        sa_type=sa.Text,
        description="Announcement body (raw HTML)",
    )
    click_count: int = sa.Field(
        default=0,
        description="Number of times users have clicked on this announcement",
    )
    close_count: int = sa.Field(
        default=0,
        description="Number of times users have dismissed this announcement",
    )
    type: str = sa.Field(
        default="info",
        description="Display type: info, warning, error, success",
    )
    is_active: bool = sa.Field(
        default=True,
        description="Whether the announcement is currently visible",
    )
    version: int = sa.Field(
        default=1,
        description="Bump to re-show a dismissed announcement",
    )
    created_by: Optional[str] = sa.Field(
        default=None,
        foreign_key="users.id",
        description="Admin who created it",
    )
