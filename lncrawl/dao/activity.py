import sqlmodel as sa

from ..enums import ActivityType
from ..utils.time_utils import current_timestamp


class UserActivity(sa.SQLModel, table=True):
    __tablename__ = "user_activities"  # type: ignore
    __table_args__ = (
        sa.Index("ix_user_activity_user_last", "user_id", "updated_at"),
        sa.Index("ix_user_activity_target", "target_id", "activity_type"),
    )

    user_id: str = sa.Field(foreign_key="users.id", ondelete="CASCADE", primary_key=True)
    activity_type: ActivityType = sa.Field(sa_type=sa.SmallInteger, primary_key=True)
    target_id: str = sa.Field(description="ID of the visited entity", primary_key=True)
    created_at: int = sa.Field(default_factory=current_timestamp, sa_type=sa.BigInteger)
    updated_at: int = sa.Field(default_factory=current_timestamp, sa_type=sa.BigInteger)
    visit_count: int = sa.Field(default=1, description="Number of visits")
