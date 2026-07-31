"""Server request/response DTOs.

Re-exported lazily via ``__getattr__`` so that importing this package only
constructs the pydantic models a given caller actually touches. The
``TYPE_CHECKING`` block keeps every name statically resolvable for pyright.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .activity import UserActivityStats
    from .announcement import AnnouncementCreateRequest, AnnouncementUpdateRequest
    from .config import ConfigProperty, ConfigSection, ConfigUpdateRequest
    from .crawler import LoginData, ProxyItem
    from .feedback import (
        Feedback,
        FeedbackCreateRequest,
        FeedbackRespondRequest,
        FeedbackUpdateRequest,
    )
    from .history import ContinueReadingResponse, ReadHistoryNovel
    from .job import (
        FetchChaptersRequest,
        FetchImagesRequest,
        FetchLatestRequest,
        FetchMissingChaptersRequest,
        FetchNovelsRequest,
        FetchVolumesRequest,
        MakeArtifactsRequest,
        SearchSourceRequest,
        TranslateChaptersRequest,
        TranslateNovelsRequest,
        TranslateVolumesRequest,
    )
    from .library import LibraryCreateRequest, LibraryItem, LibraryUpdateRequest
    from .novel import ReadChapterResponse
    from .pagination import Paginated
    from .sources import (
        AppInfo,
        CrawlerIndex,
        CrawlerInfo,
        CrawlerTestRequest,
        PRCreateRequest,
        PRResponse,
        SourceDiagnosis,
        SourceItem,
    )
    from .user import (
        CreateRequest,
        ForgotPasswordRequest,
        LoginRequest,
        LoginResponse,
        NameUpdateRequest,
        PasswordUpdateRequest,
        PutNotificationRequest,
        ResetPasswordRequest,
        SendInviteRequest,
        SignupRequest,
        TokenResponse,
        UpdateRequest,
    )

__all__ = [
    # activity
    "UserActivityStats",
    # announcement
    "AnnouncementCreateRequest",
    "AnnouncementUpdateRequest",
    # app config
    "ConfigProperty",
    "ConfigSection",
    "ConfigUpdateRequest",
    # sources
    "AppInfo",
    "CrawlerInfo",
    "CrawlerIndex",
    "CrawlerTestRequest",
    "SourceDiagnosis",
    "SourceItem",
    "PRCreateRequest",
    "PRResponse",
    # crawler
    "LoginData",
    "ProxyItem",
    # job
    "FetchNovelsRequest",
    "FetchVolumesRequest",
    "FetchChaptersRequest",
    "FetchImagesRequest",
    "FetchMissingChaptersRequest",
    "FetchLatestRequest",
    "MakeArtifactsRequest",
    "TranslateNovelsRequest",
    "TranslateVolumesRequest",
    "TranslateChaptersRequest",
    "SearchSourceRequest",
    # library
    "LibraryCreateRequest",
    "LibraryUpdateRequest",
    "LibraryItem",
    # novel
    "ReadChapterResponse",
    # pagination
    "Paginated",
    # user
    "LoginRequest",
    "TokenResponse",
    "LoginResponse",
    "SignupRequest",
    "CreateRequest",
    "UpdateRequest",
    "PasswordUpdateRequest",
    "NameUpdateRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "PutNotificationRequest",
    "SendInviteRequest",
    # feedback
    "Feedback",
    "FeedbackCreateRequest",
    "FeedbackUpdateRequest",
    "FeedbackRespondRequest",
    # history
    "ContinueReadingResponse",
    "ReadHistoryNovel",
]

# name -> submodule holding it (relative to this package)
_LAZY: dict[str, str] = {
    "UserActivityStats": ".activity",
    "AnnouncementCreateRequest": ".announcement",
    "AnnouncementUpdateRequest": ".announcement",
    "ConfigProperty": ".config",
    "ConfigSection": ".config",
    "ConfigUpdateRequest": ".config",
    "LoginData": ".crawler",
    "ProxyItem": ".crawler",
    "Feedback": ".feedback",
    "FeedbackCreateRequest": ".feedback",
    "FeedbackRespondRequest": ".feedback",
    "FeedbackUpdateRequest": ".feedback",
    "ContinueReadingResponse": ".history",
    "ReadHistoryNovel": ".history",
    "FetchChaptersRequest": ".job",
    "FetchImagesRequest": ".job",
    "FetchLatestRequest": ".job",
    "FetchMissingChaptersRequest": ".job",
    "FetchNovelsRequest": ".job",
    "FetchVolumesRequest": ".job",
    "MakeArtifactsRequest": ".job",
    "SearchSourceRequest": ".job",
    "TranslateChaptersRequest": ".job",
    "TranslateNovelsRequest": ".job",
    "TranslateVolumesRequest": ".job",
    "LibraryCreateRequest": ".library",
    "LibraryItem": ".library",
    "LibraryUpdateRequest": ".library",
    "ReadChapterResponse": ".novel",
    "Paginated": ".pagination",
    "AppInfo": ".sources",
    "CrawlerIndex": ".sources",
    "CrawlerInfo": ".sources",
    "CrawlerTestRequest": ".sources",
    "PRCreateRequest": ".sources",
    "PRResponse": ".sources",
    "SourceDiagnosis": ".sources",
    "SourceItem": ".sources",
    "CreateRequest": ".user",
    "ForgotPasswordRequest": ".user",
    "LoginRequest": ".user",
    "LoginResponse": ".user",
    "NameUpdateRequest": ".user",
    "PasswordUpdateRequest": ".user",
    "PutNotificationRequest": ".user",
    "ResetPasswordRequest": ".user",
    "SendInviteRequest": ".user",
    "SignupRequest": ".user",
    "TokenResponse": ".user",
    "UpdateRequest": ".user",
}


def __getattr__(name: str) -> Any:
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    return getattr(import_module(module, __name__), name)
