from typing import Optional

from pydantic import BaseModel, Field

from ...dao import Chapter, Job, Novel


class ReadChapterResponse(BaseModel):
    novel: Novel = Field(description="Novel details")
    chapter: Chapter = Field(description="Chapter details")
    job: Optional[Job] = Field(description="Job details")
    content: Optional[str] = Field(description="Chapter content")
    next_id: Optional[str] = Field(description="Next chapter id")
    previous_id: Optional[str] = Field(description="Previous chapter id")
    language: Optional[str] = Field(description="Current content language code (None if original)")
    word_count: Optional[int] = Field(description="Word count of the current content")
