from enum import Enum, IntEnum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from ._base import BaseModel


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserTier(IntEnum):
    BASIC = 0
    PREMIUM = 1
    VIP = 2


class User(BaseModel, table=True):
    password: str = Field(description="Hashed password", exclude=True)
    email: str = Field(unique=True, index=True, description="User Email")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    is_active: bool = Field(default=True, description="Active status")
    name: Optional[str] = Field(default=None, description="Full name")
    tier: UserTier = Field(default=UserTier.BASIC, description="User tier")


class LoginRequest(SQLModel):
    email: str = Field(description="User email")
    password: str = Field(description="User password")


class LoginResponse(SQLModel):
    token: str = Field(description="The authorization token")
    user: User = Field(description="The user")


class SignupRequest(SQLModel):
    email: EmailStr = Field(description="User Email")
    password: str = Field(description="User password")
    name: Optional[str] = Field(default=None, description="Full name")


class CreateRequest(SignupRequest):
    role: UserRole = Field(default=UserRole.USER, description="User role")
    tier: UserTier = Field(default=UserTier.BASIC, description="User tier")


class UpdateRequest(SQLModel):
    password: Optional[str] = Field(default=None, description="User password")
    name: Optional[str] = Field(default=None, description="Full name")
    role: Optional[UserRole] = Field(default=None, description="User role")
    is_active: Optional[bool] = Field(default=None, description="Active status")
    tier: Optional[UserTier] = Field(default=None, description="User tier")
