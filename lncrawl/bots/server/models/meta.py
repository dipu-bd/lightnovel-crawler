from typing import Optional

from sqlmodel import Field, SQLModel


class SupportedSource(SQLModel):
    url: str = Field(description='Source base url')
    has_manga: bool = Field(default=False)
    has_mtl: bool = Field(default=False)
    language: str = Field(default='en', description='2 letter language code')
    is_disabled: bool = Field(default=False)
    disable_reason: Optional[str] = Field(default=None)
    can_search: bool = Field(default=False)
    can_login: bool = Field(default=False)
    can_logout: bool = Field(default=False)
