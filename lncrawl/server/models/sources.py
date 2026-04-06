from functools import cached_property
from pathlib import Path
from typing import Dict, List, Optional, Type

from pydantic import BaseModel, Field

from ...context import ctx
from ...core.crawler import Crawler


class AppInfo(BaseModel):
    windows: str = Field(..., description="Windows app download URL")
    linux: str = Field(..., description="Linux app download URL")
    version: str = Field(..., description="Application version")
    home: Optional[str] = Field(None, description="Homepage URL or None")
    pypi: str = Field(..., description="PyPI release URL")


class CrawlerInfo(BaseModel):
    id: str = Field(..., description="Unique identifier")
    md5: str = Field(..., description="MD5 hash of the crawler module")
    url: str = Field(..., description="URL of the crawler module")
    version: int = Field(..., description="Version number")
    file_path: str = Field(..., description="File path of the crawler module")
    base_urls: List[str] = Field(..., description="List of base URLs")
    has_mtl: bool = Field(
        default=False, description="True if the crawler supports machine translation"
    )
    has_manga: bool = Field(default=False, description="True if the crawler supports manga")
    can_search: bool = Field(default=False, description="True if the crawler supports search")
    can_login: bool = Field(default=False, description="True if the crawler supports login")
    language: str = Field(default="en", description="2 letter language code")
    total_commits: int = Field(default=1, description="Total number of commits")
    contributors: List[str] = Field(default=[], description="List of contributors")

    @cached_property
    def user_file(self) -> Path:
        path = ctx.config.crawler.local_sources.parent
        return (path / self.file_path).absolute()

    @cached_property
    def local_file(self) -> Path:
        path = ctx.config.crawler.local_sources.parent
        return (path / self.file_path).absolute()


class CrawlerIndex(BaseModel):
    v: int = Field(..., description="Version or build number")
    app: AppInfo = Field(..., description="Application information")
    rejected: Dict[str, str] = Field(
        default_factory=dict, description="Dictionary of rejected sources"
    )
    supported: Dict[str, str] = Field(
        default_factory=dict, description="Dictionary of supported sources"
    )
    crawlers: Dict[str, CrawlerInfo] = Field(
        default_factory=dict, description="Dictionary of crawlers"
    )


class SourceItem(BaseModel):
    url: str = Field(description="Source base url")
    domain: str = Field(description="Domain name")
    version: int = Field(description="Version number")
    has_manga: bool = Field(default=False, description="True if the source supports manga")
    has_mtl: bool = Field(
        default=False, description="True if the source supports machine translation"
    )
    language: str = Field(default="en", description="2 letter language code")
    is_disabled: bool = Field(default=False, description="True if the source is disabled")
    disable_reason: Optional[str] = Field(
        default=None, description="Reason for disabling the source"
    )
    can_search: bool = Field(default=False, description="True if the source supports search")
    can_login: bool = Field(default=False, description="True if the source supports login")
    total_commits: int = Field(default=0, description="Total number of commits")
    contributors: List[str] = Field(default=[], description="List of contributors")
    total_novels: int = Field(default=0, description="Total number of novels")

    info: CrawlerInfo = Field(..., exclude=True, description="Crawler information")
    crawler: Type[Crawler] = Field(..., exclude=True, description="Crawler class")

    @cached_property
    def current_file(self):
        return Path(getattr(self.crawler, "__file__"))

    def __hash__(self) -> int:
        return hash(self.info.id)
