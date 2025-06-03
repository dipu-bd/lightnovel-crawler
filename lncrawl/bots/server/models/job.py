from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import HttpUrl
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from lncrawl.models import OutputFormat

from ._base import BaseModel
from .user import User


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "done"


class JobPriority(IntEnum):
    NORMAL = 0
    PREMIUM = 1
    VIP = 2


class RunState(str, Enum):
    PREPARING = 'preparing'
    FETCHING_NOVEL = 'fetching-novel'
    FETCHING_CONTENT = 'fetching-content'
    BINDING_NOVEL = 'binding-novel'
    UPLOADING_NOVEL = 'uploading-novel'
    FAILED = 'failed'
    SUCCESS = 'success'


class Artifact(BaseModel, table=True):
    novel_id: str = Field(foreign_key="novel.id", ondelete='CASCADE')
    novel: Optional["Novel"] = Relationship(back_populates="artifacts")

    output_file: str = Field(description="Output file path", exclude=True)
    format: OutputFormat = Field(index=True, description="The output format of the artifact")


class Novel(BaseModel, table=True):
    url: str = Field(unique=True, index=True, description="The novel page url")
    orphan: Optional[bool] = Field(default=True, exclude=True)

    title: Optional[str] = Field(default=None, description="The novel title")
    cover: Optional[str] = Field(default=None, description="The novel cover image")
    authors: Optional[str] = Field(default=None, description="The novel author")
    synopsis: Optional[str] = Field(default=None, description="The novel synopsis")
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="Tags")

    volume_count: Optional[int] = Field(default=None, description="Volume count")
    chapter_count: Optional[int] = Field(default=None, description="Chapter count")

    artifacts: List[Artifact] = Relationship()


class Job(BaseModel, table=True):
    user_id: str = Field(foreign_key="user.id", ondelete='CASCADE')
    user: Optional[User] = Relationship()

    novel_id: Optional[str] = Field(foreign_key="novel.id", ondelete='SET NULL')
    novel: Optional[Novel] = Relationship()

    url: str = Field(description="Download link")

    priority: JobPriority = Field(default=JobPriority.NORMAL, index=True, description="The job priority")
    status: JobStatus = Field(default=JobStatus.PENDING, index=True, description="Current status")
    run_state: Optional[RunState] = Field(default=None, description="State of the job in progress status")

    progress: int = Field(default=0, description="Download progress percentage")
    error: Optional[str] = Field(default=None, description='Error state in case of failure')
    started_at: Optional[int] = Field(default=None, description="Job start time (UNIX ms)")
    finished_at: Optional[int] = Field(default=None, description="Job finish time (UNIX ms)")


class JobInput(SQLModel):
    priority: JobPriority = Field(default=JobPriority.NORMAL, description="The job priority")
    url: HttpUrl = Field(description='The novel page url')


class JobDetail(SQLModel):
    job: Job = Field(description='Job')
    user: Optional[User] = Field(description='User')
    novel: Optional[Novel] = Field(description='Novel')
    artifacts: Optional[List[Artifact]] = Field(description='Artifacts')
