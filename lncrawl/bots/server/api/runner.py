from fastapi import APIRouter, Depends

from ..context import ServerContext
from ..models.job import JobRunnerStatus

# The root router
router = APIRouter()


@router.get("/status", summary='Get runner status')
def running(ctx: ServerContext = Depends()) -> JobRunnerStatus:
    return JobRunnerStatus(
        running=ctx.scheduler.running,
        history=list(reversed(ctx.scheduler.history)),
    )


@router.post("/start", summary='Start the runner')
def start(ctx: ServerContext = Depends()) -> bool:
    ctx.scheduler.start()
    return True


@router.post("/stop", summary='Stops the runner')
def stop(ctx: ServerContext = Depends()) -> bool:
    ctx.scheduler.stop()
    return True
