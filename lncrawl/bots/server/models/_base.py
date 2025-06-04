import uuid

from sqlalchemy import event
from sqlmodel import Field, SQLModel

from ..utils.time_utils import current_timestamp


def generate_uuid():
    return uuid.uuid4().hex


class BaseModel(SQLModel):
    id: str = Field(
        default_factory=generate_uuid,
        primary_key=True,
        description="ID"
    )
    created_at: int = Field(
        index=True,
        default_factory=current_timestamp,
        description="Create timestamp (ms)"
    )
    updated_at: int = Field(
        default_factory=current_timestamp,
        description="Update timestamp (ms)"
    )


@event.listens_for(BaseModel, "before_update", propagate=True)
def auto_update_timestamp(mapper, connection, target: BaseModel):
    target.updated_at = current_timestamp()
