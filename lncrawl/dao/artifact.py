from typing import Optional

import sqlmodel as sa
from pydantic import computed_field

from ..context import ctx
from ._base import BaseTable
from .enums import OutputFormat


class Artifact(BaseTable, table=True):
    __tablename__ = "artifacts"  # type: ignore

    novel_id: str = sa.Field(index=True, foreign_key="novels.id", ondelete="CASCADE")
    job_id: Optional[str] = sa.Field(foreign_key="jobs.id", ondelete="SET NULL")
    user_id: Optional[str] = sa.Field(foreign_key="users.id", ondelete="SET NULL")
    format: OutputFormat = sa.Field(index=True, description="The output format of the artifact")
    file_name: str = sa.Field(description="Artifact output file name")
    file_size: int = sa.Field(
        default=0, sa_type=sa.BigInteger, description="Artifact output file size in bytes"
    )

    @computed_field  # type: ignore[misc]
    @property
    def output_file(self) -> str:
        """Artifact file path"""
        return f"novels/{self.novel_id}/artifacts/{self.file_name}"

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        """Content file is available"""
        return ctx.files.exists(self.output_file)
