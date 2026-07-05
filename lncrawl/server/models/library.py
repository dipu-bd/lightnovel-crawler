from typing import Optional

from pydantic import BaseModel, Field, computed_field

from ...context import ctx


class LibraryCreateRequest(BaseModel):
    name: str = Field(description="Library name")
    description: Optional[str] = Field(default=None, description="Library description")
    is_public: bool = Field(default=False, description="Is public")


class LibraryUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, description="Library name")
    description: Optional[str] = Field(default=None, description="Library description")
    is_public: Optional[bool] = Field(default=None, description="Is public")


class LibraryItem(BaseModel):
    id: str = Field(description="Library ID")
    name: str = Field(description="Library name")
    description: Optional[str] = Field(default=None, description="Library description")
    cover_file: Optional[str] = Field(default=None, description="First novel cover if available")
    is_public: bool = Field(description="Is public")

    @computed_field  # type: ignore[misc]
    @property
    def cover_available(self) -> bool:
        """Whether the cover image file is available"""
        return self.cover_file is not None and ctx.files.exists(self.cover_file)
