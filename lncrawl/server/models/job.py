from typing import List, Optional

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
