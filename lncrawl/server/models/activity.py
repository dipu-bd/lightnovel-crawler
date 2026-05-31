from typing import Dict, Optional

from pydantic import BaseModel, Field

from ...enums import ActivityType


class UserActivityStats(BaseModel):
    last_activity: Optional[int] = Field(default=None, description="Timestamp of last activity")
    activity_count: int = Field(default=0, description="Total number of activities")
    visits: Dict[ActivityType, int] = Field(
        default_factory=dict, description="Visit count per activity type"
    )
