import sqlmodel as sa

from ..utils.time_utils import current_timestamp


class Secret(sa.SQLModel, table=True):
    __tablename__ = "secrets"  # type: ignore

    user_id: str = sa.Field(index=True, foreign_key="users.id", ondelete="CASCADE")
    name: str = sa.Field(
        primary_key=True, index=True, nullable=False, max_length=255, description="Secret name"
    )
    value: bytes = sa.Field(
        exclude=True, sa_type=sa.LargeBinary, description="Encrypted secret value"
    )
    created_at: int = sa.Field(index=True, default_factory=current_timestamp, sa_type=sa.BigInteger)
