from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import JSON, Column, Field, SQLModel

from ..utils.time_utils import current_timestamp
from ._base import BaseTable
from .enums import UserRole, UserTier


class User(BaseTable, table=True):
    password: str = Field(description="Hashed password", exclude=True)
    email: str = Field(unique=True, index=True, description="User Email")
    name: Optional[str] = Field(default=None, description="Full name")

    role: UserRole = Field(default=UserRole.USER, description="User role")
    tier: UserTier = Field(default=UserTier.BASIC, description="User tier")
    is_active: bool = Field(default=True, description="Active status")

    extra: Dict[str, Any] = Field(default={}, sa_column=Column(JSON), description="Extra field")


class VerifiedEmail(SQLModel, table=True):
    email: str = Field(primary_key=True, description="User Email")
    created_at: int = Field(default_factory=current_timestamp)


class LoginRequest(BaseModel):
    email: str = Field(description="User email")
    password: str = Field(description="User password")


class TokenResponse(BaseModel):
    token: str = Field(description="The authorization token")


class LoginResponse(TokenResponse):
    user: User = Field(description="The user")
    is_verified: bool = Field(description="Is the email verified")


class SignupRequest(BaseModel):
    email: EmailStr = Field(description="User Email")
    password: str = Field(description="User password")
    name: Optional[str] = Field(default=None, description="Full name")


class CreateRequest(SignupRequest):
    role: UserRole = Field(default=UserRole.USER, description="User role")
    tier: UserTier = Field(default=UserTier.BASIC, description="User tier")


class UpdateRequest(BaseModel):
    password: Optional[str] = Field(default=None, description="User password")
    name: Optional[str] = Field(default=None, description="Full name")
    role: Optional[UserRole] = Field(default=None, description="User role")
    is_active: Optional[bool] = Field(default=None, description="Active status")
    tier: Optional[UserTier] = Field(default=None, description="User tier")
