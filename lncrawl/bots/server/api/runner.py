from fastapi import APIRouter, Depends

from ..context import ServerContext

# The root router
router = APIRouter()


@router.get("/start", summary='Start the runner')
def start(ctx: ServerContext = Depends()):
    ctx.scheduler.start()


@router.get("/stop", summary='Stops the runner')
def stop(ctx: ServerContext = Depends()):
    ctx.scheduler.close()
