from typing import Optional

import sqlmodel as sa

from ._base import BaseTable
from .enums import FeedbackStatus, FeedbackType


class Feedback(BaseTable, table=True):
    __tablename__ = "feedback"  # type: ignore
    __table_args__ = (
        sa.Index("ix_feedback_user_id", "user_id"),
        sa.Index("ix_feedback_status", "status"),
        sa.Index("ix_feedback_type", "type"),
        sa.Index("ix_feedback_created_at", "created_at"),
    )

    user_id: str = sa.Field(
        foreign_key="users.id", ondelete="CASCADE", description="User who submitted the feedback"
    )
    type: FeedbackType = sa.Field(description="Type of feedback")
    status: FeedbackStatus = sa.Field(
        default=FeedbackStatus.PENDING, description="Current status of the feedback"
    )
    subject: str = sa.Field(description="Subject/title of the feedback")
    message: str = sa.Field(sa_type=sa.Text, description="Detailed message/description")
    admin_notes: Optional[str] = sa.Field(
        default=None, sa_type=sa.Text, description="Admin notes/response"
    )
