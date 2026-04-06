from typing import Optional

from fastapi import APIRouter, Body, Path, Query, Security

from ...context import ctx
from ...dao import Job, JobPriority, JobStatus, JobType, User, UserTier
from ...exceptions import ServerErrors
from ..models import (
    FetchChaptersRequest,
    FetchImagesRequest,
    FetchNovelRequest,
    FetchNovelsRequest,
    FetchVolumesRequest,
    MakeArtifactsRequest,
    Paginated,
)
from ..security import ensure_user
from ..tier import ENABLED_FORMATS

# The root router
router = APIRouter()


@router.get("s", summary="Returns a list of jobs")
def list_jobs(
    user: User = Security(ensure_user),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    type: Optional[JobType] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    status: Optional[JobStatus] = Query(default=None),
    priority: Optional[JobPriority] = Query(default=None),
    parent_job_id: Optional[str] = Query(default=None),
    is_done: Optional[bool] = Query(default=None),
) -> Paginated[Job]:
    return ctx.jobs.list(
        limit=limit,
        offset=offset,
        user_id=user_id,
        job_type=type,
        status=status,
        is_done=is_done,
        priority=priority,
        parent_job_id=parent_job_id,
    )


@router.delete("/{job_id}", summary="Deletes a job")
def delete_job(
    user: User = Security(ensure_user),
    job_id: str = Path(),
) -> bool:
    ctx.jobs.verify_access(user, job_id)
    ctx.scheduler.stop_job(job_id)
    ctx.jobs.delete(job_id)
    return True


@router.get("/{job_id}", summary="Gets job details")
def get_job(
    job_id: str = Path(),
) -> Job:
    return ctx.jobs.get(job_id)


@router.post("/{job_id}/cancel", summary="Cancel a job")
def cancel_job(
    user: User = Security(ensure_user),
    job_id: str = Path(),
) -> bool:
    user_id = ctx.jobs.verify_access(user, job_id)
    who = "user" if user.id == user_id else "admin"
    ctx.scheduler.stop_job(job_id)
    ctx.jobs.cancel(job_id, who)
    return True


@router.post("/{job_id}/replay", summary="Replay a job")
def replay_job(
    user: User = Security(ensure_user),
    job_id: str = Path(),
) -> Job:
    job = ctx.jobs.get(job_id)
    return ctx.jobs._create(
        user=user,
        type=job.type,
        data=job.extra,
        depends_on=job.depends_on,
    )


@router.post("/create/fetch-novel", summary="Create a job to fetch entire novel")
def fetch_novel(
    user: User = Security(ensure_user),
    body: FetchNovelRequest = Body(),
) -> Job:
    url = str(body.url)
    return ctx.jobs.fetch_novel(user, url, full=body.full)


@router.post("/create/fetch-novels", summary="Create a job to fetch multiple novels")
def fetch_novels(
    user: User = Security(ensure_user),
    body: FetchNovelsRequest = Body(),
) -> Job:
    urls = [str(url) for url in body.urls]
    if body.full and user.tier == UserTier.BASIC:
        raise ServerErrors.full_novel_not_allowed
    return ctx.jobs.fetch_many_novels(user, *urls, full=body.full)


@router.post(
    "/create/fetch-volumes", summary="Create a job to fetch all chapter contents for the volumes"
)
def fetch_volumes(
    user: User = Security(ensure_user),
    body: FetchVolumesRequest = Body(),
) -> Job:
    volumes = list(set(body.volumes))
    if not volumes:
        raise ServerErrors.no_volumes_to_download
    if len(volumes) == 1:
        return ctx.jobs.fetch_volume(user, volumes[0])
    return ctx.jobs.fetch_many_volumes(user, *volumes)


@router.post("/create/fetch-chapters", summary="Create a job to fetch chapter contents")
def fetch_chapters(
    user: User = Security(ensure_user),
    body: FetchChaptersRequest = Body(),
) -> Job:
    chapters = list(set(body.chapters))
    if not chapters:
        raise ServerErrors.no_chapters_to_download
    if len(chapters) == 1:
        return ctx.jobs.fetch_chapter(user, chapters[0])
    return ctx.jobs.fetch_many_chapters(user, *chapters)


@router.post("/create/fetch-images", summary="Create a job to fetch chapter images")
def fetch_images(
    user: User = Security(ensure_user),
    body: FetchImagesRequest = Body(),
) -> Job:
    images = list(set(body.images))
    if not images:
        raise ServerErrors.no_images_to_download
    if len(images) == 1:
        return ctx.jobs.fetch_image(user, images[0])
    return ctx.jobs.fetch_many_images(user, *images)


@router.post("/create/make-artifacts", summary="Create a job to make novel artifacts")
def make_artifacts(user: User = Security(ensure_user), body: MakeArtifactsRequest = Body()) -> Job:
    formats = set(body.formats) & ENABLED_FORMATS[user.tier]
    if len(formats) == 0:
        raise ServerErrors.no_artifacts_to_create
    return ctx.jobs.make_many_artifacts(user, body.novel_id, *formats)
