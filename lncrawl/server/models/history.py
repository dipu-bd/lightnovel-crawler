from typing import Optional

from pydantic import BaseModel, Field


class ContinueReadingResponse(BaseModel):
    chapter_id: Optional[str] = Field(
        description="Chapter to (re)start reading from; None if the novel has no chapters"
    )
    has_history: bool = Field(description="Whether the user has read any chapter of this novel")
