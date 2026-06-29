from typing import Dict, Optional

from pydantic import BaseModel, Field

from ...enums import ActivityType


class UserActivityStats(BaseModel):
    last_activity: Optional[int] = Field(default=None, description="Timestamp of last activity")
    activity_count: int = Field(default=0, description="Total number of activities")
    visits: Dict[ActivityType, int] = Field(
        default_factory=dict, description="Visit count per activity type"
    )


class DailyActiveUsers(BaseModel):
    date: str  # "YYYY-MM-DD"
    users: int


class DailyTypeCount(BaseModel):
    date: str
    activity_type: ActivityType
    events: int


class GlobalActivitySummary(BaseModel):
    total_users: int
    active_users: int
    total_events: int
    by_type: Dict[ActivityType, int]
    dau: int = Field(default=0, description="Distinct users active in the trailing 1 day")
    mau: int = Field(default=0, description="Distinct users active in the trailing 30 days")
    new_users: int = Field(
        default=0, description="Users whose first-ever activity falls within the window"
    )


class TopUserActivity(BaseModel):
    user_id: str
    username: str
    email: str
    total: int
    by_type: Dict[ActivityType, int]


class TopNovelActivity(BaseModel):
    novel_id: str
    title: str
    visits: int = Field(description="Total visit count across all users")
    readers: int = Field(description="Distinct users who visited this novel")


class EngagementBucket(BaseModel):
    bucket: str = Field(description="Events-per-user range label, e.g. '2-5'")
    users: int = Field(description="Number of active users falling in this range")


class HourlyActivityCell(BaseModel):
    dow: int = Field(description="Day of week, 0=Sunday .. 6=Saturday")
    hour: int = Field(description="Hour of day, 0..23, in the requested timezone")
    events: int = Field(description="Number of activity records last touched in this window")
