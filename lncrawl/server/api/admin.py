from typing import List, Literal, Union

from fastapi import APIRouter, Body, Query

from ...context import ctx
from ..models import (
    ConfigSection,
    ConfigUpdateRequest,
)
from ..models.activity import (
    DailyActiveUsers,
    DailyTypeCount,
    EngagementBucket,
    GlobalActivitySummary,
    HourlyActivityTotal,
    TopNovelActivity,
    TopUserActivity,
)

# The root router
router = APIRouter()


@router.post("/update-sources", summary="Update sources from the repository")
async def update() -> int:
    return ctx.admin.update_sources()


@router.post("/soft-restart", summary="Reload application context and restart the scheduler")
def soft_restart() -> None:
    ctx.admin.soft_restart()


@router.get("/runner/status", summary="Get runner status")
def status() -> bool:
    return bool(ctx.scheduler.running)


@router.post("/runner/start", summary="Start the runner")
def start() -> bool:
    ctx.scheduler.start()
    return True


@router.post("/runner/stop", summary="Stops the runner")
def stop() -> bool:
    ctx.scheduler.stop()
    return True


@router.get(
    "/configs",
    summary="List application configs",
)
def list_configs() -> List[ConfigSection]:
    return ctx.admin.config_sections()


@router.patch(
    "/configs",
    summary="Update application configs",
)
def patch_configs(
    body: List[ConfigUpdateRequest] = Body(...),
) -> None:
    ctx.admin.update_config(body)


ActivityDataType = Literal[
    "summary",
    "dau",
    "type-trend",
    "top-users",
    "top-novels",
    "engagement",
    "hourly-heatmap",
]


@router.get("/activity", summary="Get admin activity dashboard data", response_model=None)
def get_activity_data(
    type: ActivityDataType = Query(..., description="Which dataset to return"),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=20, ge=1, le=100),  # only used when type="top-users"
    tz_offset: int = Query(
        default=0,
        ge=-720,
        le=840,
        description="Minutes to add to UTC for hourly-heatmap bucketing (= -Date.getTimezoneOffset())",
    ),
) -> Union[
    GlobalActivitySummary,
    List[DailyActiveUsers],
    List[DailyTypeCount],
    List[TopUserActivity],
    List[TopNovelActivity],
    List[EngagementBucket],
    List[HourlyActivityTotal],
]:
    if type == "summary":
        return ctx.activity.get_admin_summary(days)
    elif type == "dau":
        return ctx.activity.get_admin_dau(days)
    elif type == "type-trend":
        return ctx.activity.get_admin_type_trend(days)
    elif type == "top-novels":
        return ctx.activity.get_admin_top_novels(days, limit)
    elif type == "engagement":
        return ctx.activity.get_admin_engagement(days)
    elif type == "hourly-heatmap":
        return ctx.activity.get_admin_hourly_totals(days, tz_offset)
    else:
        return ctx.activity.get_admin_top_users(days, limit)
