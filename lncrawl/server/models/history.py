from typing import Optional

from pydantic import BaseModel, Field

from ...dao import Novel


class ContinueReadingResponse(BaseModel):
    chapter_id: Optional[str] = Field(
        description="Chapter to (re)start reading from; None if the novel has no chapters"
    )
    has_history: bool = Field(description="Whether the user has read any chapter of this novel")


class ReadHistoryNovel(BaseModel):
    novel: Novel = Field(description="The novel that was read")
    last_read_at: int = Field(description="Timestamp of the most recent read chapter")
    last_chapter_id: Optional[str] = Field(
        default=None, description="Most recently read chapter; resume target for the reader"
    )
    read_count: int = Field(description="Number of chapters of this novel the user has read")
