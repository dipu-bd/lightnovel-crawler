from typing import Dict, List, Optional

from pydantic import BaseModel, Field, computed_field

from ...core.tiers import LEGACY
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

    request_rate_limit: float = Field(
        default=3, description="Max requests per second to this source"
    )

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
    # On SourceItem rather than on _CommonSourceInfo, because CrawlerInfo is the published
    # index's wire format and must stay byte-identical for clients that only know the old one.
    tier: str = Field(
        default=LEGACY,
        description="Which tier serves this host: 'spec' for a declarative definition, "
        "'legacy' for a Python crawler. Decides precedence when both exist.",
    )

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


class SourceDiagnosis(BaseModel):
    """Why a source is or is not working, as far as anything here knows.

    Two independent halves, because the two failures they describe are told apart
    nowhere else: what the scraper concluded about the site's defences, and what the
    crawl itself observed. A source can be perfectly reachable and still return
    nothing, which is what `health` is for.
    """

    domain: str = Field(..., description="Source domain")
    url: str = Field(default="", description="Source base URL")
    rejected: Optional[str] = Field(
        default=None, description="Why the domain is rejected, if it is"
    )
    is_disabled: bool = Field(default=False, description="True if the source is disabled")
    disable_reason: Optional[str] = Field(default=None, description="Reason for disabling")

    known: bool = Field(
        default=False, description="False when nothing has been learned about this origin yet"
    )
    binding_layer: Optional[int] = Field(
        default=None, description="Detection layer last found to be binding"
    )
    binding_layer_name: Optional[str] = Field(default=None, description="Name of that layer")
    reads: Optional[str] = Field(
        default=None,
        description="What the binding layer reads: emit, possess, hybrid or outside",
    )
    stance: Optional[str] = Field(
        default=None, description="What the scraper does about that layer"
    )
    summary: Optional[str] = Field(default=None, description="What the binding layer is")
    tier: str = Field(default="", description="Capability set that last succeeded")
    interval: float = Field(default=0.0, description="Learned seconds between requests")
    successes: int = Field(default=0, description="Successful requests recorded")
    failures: int = Field(default=0, description="Failed requests recorded")
    consecutive_failures: int = Field(default=0, description="Failures since the last success")
    has_clearance: bool = Field(default=False, description="True if a browser clearance is held")

    health: Dict[str, int] = Field(
        default_factory=dict,
        description="Count per reason a crawl needed more than a plain fetch, this run",
    )
    samples: Dict[str, List[str]] = Field(
        default_factory=dict, description="A few examples per health reason"
    )
    explain: str = Field(default="", description="The scraper's own account of this origin")
