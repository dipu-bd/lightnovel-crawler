from enum import Enum, IntEnum
from typing import List, Optional

from sqlalchemy import event
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from lncrawl.models import OutputFormat

from ..utils.time_utils import current_timestamp
from ._base import BaseModel
from .user import User


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "done"


class JobPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class RunState(IntEnum):
    FETCHING_NOVEL = 0
    FETCHING_CHAPTERS = 1
    FETCHING_IMAGES = 2
    CREATING_ARTIFACTS = 3
    FAILED = 4
    SUCCESS = 5
    CANCELED = 6


class Artifact(BaseModel, table=True):
    novel_id: str = Field(foreign_key="novel.id", ondelete='CASCADE')
    novel: Optional["Novel"] = Relationship(back_populates="artifacts")

    file_name: str = Field(description="Output file name")
    output_file: str = Field(description="Output file path", exclude=True)
    format: OutputFormat = Field(index=True, description="The output format of the artifact")


class Novel(BaseModel, table=True):
    url: str = Field(unique=True, index=True, description="The novel page url")
    orphan: Optional[bool] = Field(default=True, exclude=True)

    title: Optional[str] = Field(default=None, description="The novel title")
    cover: Optional[str] = Field(default=None, description="The novel cover image", exclude=True)
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

    priority: JobPriority = Field(default=JobPriority.LOW, index=True, description="The job priority")
    status: JobStatus = Field(default=JobStatus.PENDING, index=True, description="Current status")
    run_state: Optional[RunState] = Field(default=None, description="State of the job in progress status")

    progress: int = Field(default=0, description="Download progress percentage")
    error: Optional[str] = Field(default=None, description='Error state in case of failure')
    started_at: Optional[int] = Field(default=None, description="Job start time (UNIX ms)")
    finished_at: Optional[int] = Field(default=None, description="Job finish time (UNIX ms)")


@event.listens_for(Job, "before_update", propagate=True)
def auto_update_timestamp(mapper, connection, target: Job):
    if target.error and target.run_state:
        if target.error.startswith('Canceled'):
            target.run_state = RunState.CANCELED
        else:
            target.run_state = RunState.FAILED
    if not target.started_at and target.status != JobStatus.PENDING:
        target.started_at = current_timestamp()
    if not target.finished_at and target.status == JobStatus.COMPLETED:
        target.finished_at = current_timestamp()


class JobDetail(SQLModel):
    job: Job = Field(description='Job')
    novel: Optional[Novel] = Field(description='Novel')
    artifacts: Optional[List[Artifact]] = Field(description='Artifacts')
    user: Optional[User] = Field(description='User')


class JobRunnerHistoryItem(SQLModel):
    time: int = Field(description='UNIX timestamp (seconds)')
    job_id: str = Field(description='Job')
    user_id: str = Field(description='User')
    novel_id: Optional[str] = Field(description='Novel')
    status: JobStatus = Field(description="Current status")
    run_state: Optional[RunState] = Field(description="State of the job in progress status")


class JobRunnerStatus(SQLModel):
    running: bool = Field(description='Job runner status')
    history: List[JobRunnerHistoryItem] = Field(description='Runner history')
