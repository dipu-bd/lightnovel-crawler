from typing import Optional

from pydantic import BaseModel


class AnnouncementCreateRequest(BaseModel):
    type: str = "info"
    title: str = ""
    message: Optional[str] = None
    is_active: bool = False


class AnnouncementUpdateRequest(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    bump_version: bool = False
