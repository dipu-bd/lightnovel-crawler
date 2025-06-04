from fastapi import APIRouter, Depends

from ..context import ServerContext
from ..models.job import JobRunnerStatus

# The root router
router = APIRouter()


@router.get("/status", summary='Get runner status')
def running(ctx: ServerContext = Depends()):
    return JobRunnerStatus(
        running=ctx.scheduler.running,
        history=list(reversed(ctx.scheduler.history)),
    )


@router.post("/start", summary='Start the runner')
def start(ctx: ServerContext = Depends()):
    ctx.scheduler.start()


@router.post("/stop", summary='Stops the runner')
def stop(ctx: ServerContext = Depends()):
    ctx.scheduler.stop()
