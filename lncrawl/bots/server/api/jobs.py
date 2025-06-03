from typing import Optional

from fastapi import APIRouter, Body, Depends, Path, Query

from ..context import ServerContext
from ..models.job import JobInput, JobPriority, JobStatus
from ..models.user import User, UserRole
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
):
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
def create_job(
    input: JobInput = Body(),
    ctx: ServerContext = Depends(),
    user: User = Depends(ensure_user),
):
    if user.role != UserRole.ADMIN:
        input.priority = JobPriority.NORMAL
    return ctx.jobs.create(input, user)


@router.delete("/{job_id}", summary='Deletes a job')
def delete_job(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
    user: User = Depends(ensure_user),
):
    return ctx.jobs.delete(job_id, user)


@router.get("/{job_id}", summary='Returns a job')
def get_job(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
):
    return ctx.jobs.get(job_id)


@router.get("/{job_id}/novel", summary='Returns a job novel')
def get_job_novel(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
):
    return ctx.jobs.get_novel(job_id)


@router.get("/{job_id}/artifacts", summary='Returns job artifacts')
def get_job_artifacts(
    job_id: str = Path(),
    ctx: ServerContext = Depends(),
):
    return ctx.jobs.get_artifacts(job_id)
