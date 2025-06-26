import uuid

from sqlalchemy import event
from sqlmodel import Field, SQLModel, BigInteger

from ..utils.time_utils import current_timestamp


def generate_uuid():
    return uuid.uuid4().hex


class BaseTable(SQLModel):
    id: str = Field(
        default_factory=generate_uuid,
        primary_key=True,
        description="ID"
    )
    created_at: int = Field(default_factory=current_timestamp, sa_type=BigInteger)
    updated_at: int = Field(default_factory=current_timestamp, sa_type=BigInteger)


@event.listens_for(BaseTable, "before_update", propagate=True)
def auto_update_timestamp(mapper, connection, target: BaseTable):
    target.updated_at = current_timestamp()
