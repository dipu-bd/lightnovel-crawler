from typing import Dict, List, Optional

from pydantic import BaseModel, Field, computed_field

from ...utils.github import GithubClient


class AppInfo(BaseModel):
    windows: str = Field(..., description="Windows app download URL")
    linux: str = Field(..., description="Linux app download URL")
    version: str = Field(..., description="Application version")
    home: Optional[str] = Field(None, description="Homepage URL or None")
    pypi: str = Field(..., description="PyPI release URL")


class _CommonSourceInfo(BaseModel):
    version: int = Field(..., description="Version number")
    md5: str = Field(..., description="MD5 hash of the crawler file")
    file_path: str = Field(..., description="File path of the crawler module")

    language: str = Field("en", description="2 letter language code")
    has_manga: bool = Field(default=False, description="True if source has manga")
    can_login: bool = Field(default=False, description="True if crawler supports login")
    can_search: bool = Field(default=False, description="True if crawler supports search")
    has_mtl: bool = Field(default=False, description="True if source has machine translation")

    total_commits: int = Field(default=1, description="Total number of commits")
    contributors: List[str] = Field(default=[], description="List of contributors")

    @computed_field  # type: ignore[misc]
    @property
    def github_url(self) -> str:
        return GithubClient.get_remote_view_link(self.file_path)


class CrawlerInfo(_CommonSourceInfo):
    id: str = Field(..., description="Crawler ID")
    base_urls: List[str] = Field(..., description="List of base URLs")

    def __hash__(self) -> int:
        return hash(self.id)


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


class SourceItem(_CommonSourceInfo):
    url: str = Field(..., description="Source base url")
    domain: str = Field(..., description="Domain name")
    crawler_id: str = Field(..., description="Crawler ID")
    total_novels: int = Field(default=0, description="Total number of novels")
    is_disabled: bool = Field(default=False, description="True if the source is disabled")
    disable_reason: Optional[str] = Field(default=None, description="Reason for disabling")

    def __hash__(self) -> int:
        return hash(self.domain)


class CrawlerTestRequest(BaseModel):
    url: str = Field(..., description="Novel URL to fetch with the crawler")
    content: str = Field(..., description="Crawler source code to test")


class PRCreateRequest(BaseModel):
    title: str = Field(default="", description="Commit message and PR title")
    body: str = Field(default="", description="PR description body")
    content: str = Field(..., description="Updated file content")


class PRResponse(BaseModel):
    url: str = Field(description="PR URL")
    number: int = Field(description="PR number")
    branch: str = Field(description="PR branch name")
