from typing import List, Optional

from fastapi import APIRouter, Depends, Form, Path, Query, Security
from pydantic import HttpUrl

from ..context import ServerContext
from ..models.enums import JobPriority, JobStatus
from ..models.job import Job, JobDetail
from ..models.novel import Artifact, Novel
from ..models.pagination import Paginated
from ..models.user import User
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("s", summary='Returns a list of jobs')
def list_jobs(
    ctx: ServerContext = Depends(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc", regex="^(asc|desc)$"),
    user_id: Optional[str] = Query(default=None),
    novel_id: Optional[str] = Query(default=None),
    status: Optional[JobStatus] = Query(default=None),
    priority: Optional[JobPriority] = Query(default=None),
) -> Paginated[Job]:
    return ctx.jobs.list(
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
        status=status,
        priority=priority,
        user_id=user_id,
        novel_id=novel_id,
    )


@router.post("", summary='Creates a new job')
async def create_job(
    ctx: ServerContext = Depends(),
    user: User = Security(ensure_user),
    url: HttpUrl = Form(description='The novel page url'),
) -> Job:
    job = await ctx.jobs.create(url, user)
    return job


@router.delete("/{job_id}", summary='Deletes a job')
def delete_job(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
    user: User = Security(ensure_user),
) -> bool:
    return ctx.jobs.delete(job_id, user)


@router.get("/{job_id}", summary='Returns a job')
def get_job(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> JobDetail:
    return ctx.jobs.get(job_id)


@router.post("/{job_id}/cancel", summary='Cancel a job')
def cancel_job(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
    user: User = Security(ensure_user),
) -> bool:
    return ctx.jobs.cancel(job_id, user)


@router.get("/{job_id}/novel", summary='Returns a job novel')
def get_job_novel(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> Novel:
    return ctx.jobs.get_novel(job_id)


@router.get("/{job_id}/artifacts", summary='Returns job artifacts')
def get_job_artifacts(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> List[Artifact]:
    return ctx.jobs.get_artifacts(job_id)
