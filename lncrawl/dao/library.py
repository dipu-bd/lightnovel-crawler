from typing import Optional

from pydantic import computed_field
import sqlmodel as sa

from ..context import ctx
from ..utils.time_utils import current_timestamp
from ._base import BaseTable


class Library(BaseTable, table=True):
    __tablename__ = "libraries"  # type: ignore

    user_id: str = sa.Field(
        foreign_key="users.id",
        description="Owner user id",
        ondelete="CASCADE",
        index=True,
    )

    name: str = sa.Field(
        description="Library name",
        index=True,
    )
    description: Optional[str] = sa.Field(default=None, description="Library description")
    is_public: bool = sa.Field(default=False, description="Is library visible to everyone")

    @computed_field  # type: ignore[misc]
    @property
    def cover_file(self) -> Optional[str]:
        """Cover image file path"""
        return self.extra.get("novel_cover")

    @computed_field  # type: ignore[misc]
    @property
    def cover_available(self) -> bool:
        """Whether the cover image file is available"""
        return self.cover_file is not None and ctx.files.exists(self.cover_file)


class LibraryNovel(sa.SQLModel, table=True):
    __tablename__ = "library_novels"  # type: ignore

    library_id: str = sa.Field(
        foreign_key="libraries.id",
        primary_key=True,
        ondelete="CASCADE",
        description="Library id",
    )
    novel_id: str = sa.Field(
        foreign_key="novels.id",
        primary_key=True,
        ondelete="CASCADE",
        description="Novel id",
    )


class LibraryFavorite(sa.SQLModel, table=True):
    __tablename__ = "library_favorites"  # type: ignore

    user_id: str = sa.Field(
        foreign_key="users.id",
        primary_key=True,
        ondelete="CASCADE",
        description="User who favorited the library",
    )
    library_id: str = sa.Field(
        foreign_key="libraries.id",
        primary_key=True,
        ondelete="CASCADE",
        description="Favorited library id",
    )
    created_at: int = sa.Field(
        default_factory=current_timestamp,
        sa_type=sa.BigInteger,
    )
