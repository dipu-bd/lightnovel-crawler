from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

from ...dao import LanguageCode, OutputFormat


class FetchNovelsRequest(BaseModel):
    urls: List[HttpUrl] = Field(description="List of urls to fetch")
    full: bool = Field(default=False, description="To fetch all contents")


class FetchVolumesRequest(BaseModel):
    volumes: List[str] = Field(description="List of volume ids to fetch")


class FetchChaptersRequest(BaseModel):
    chapters: List[str] = Field(description="List of chapter ids to fetch")


class FetchImagesRequest(BaseModel):
    images: List[str] = Field(description="List of image ids to fetch")


class MakeArtifactsRequest(BaseModel):
    novel_id: str = Field(description="The novel id")
    formats: List[OutputFormat] = Field(description="List of formats")
    language: Optional[LanguageCode] = Field(default=None, description="Target language code")
    scope_mode: Literal["by_volume", "volume_ids", "volume_range", "chapter_range"] = Field(
        default="by_volume",
        description="How to split the requested artifacts",
    )
    volume_ids: List[str] = Field(
        default_factory=list,
        description="Volume ids to include when scope mode is volume_ids",
    )
    from_volume: Optional[int] = Field(
        default=None,
        description="First volume serial when scope mode is volume_range",
    )
    to_volume: Optional[int] = Field(
        default=None,
        description="Last volume serial when scope mode is volume_range",
    )
    from_chapter: Optional[int] = Field(
        default=None,
        description="First chapter serial when scope mode is chapter_range",
    )
    to_chapter: Optional[int] = Field(
        default=None,
        description="Last chapter serial when scope mode is chapter_range",
    )


class TranslateNovelsRequest(BaseModel):
    novel_ids: List[str] = Field(description="List of novel ids to translate")
    language: LanguageCode = Field(description="Target language code")
    full: bool = Field(default=False, description="Also translate all volumes and chapters")


class TranslateVolumesRequest(BaseModel):
    volumes: List[str] = Field(description="List of volume ids to translate")
    language: LanguageCode = Field(description="Target language code")


class TranslateChaptersRequest(BaseModel):
    chapters: List[str] = Field(description="List of chapter ids to translate")
    language: LanguageCode = Field(description="Target language code")
