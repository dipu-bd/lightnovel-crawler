import logging
import traceback
from typing import Any, Optional
from urllib.error import URLError

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from PIL import UnidentifiedImageError
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError

from .cloudscraper.exceptions import AbortedException, CloudflareException

__all__ = [
    "LNException",
    "ServerError",
    "ServerErrors",
    "WebSocketError",
    "WebSocketErros",
    "AbortedException",
    "RetryErrorGroup",
    "ScraperErrorGroup",
    "FallbackToBrowser",
    "get_exception_handlers",
]


class LNException(Exception):
    pass


class FallbackToBrowser(Exception):
    pass


ScraperErrorGroup = (
    URLError,
    HTTPError,
    CloudflareException,
    RequestException,
    FallbackToBrowser,
    UnidentifiedImageError,
)

RetryErrorGroup = (
    URLError,
    HTTPError,
    CloudflareException,
    RequestException,
    UnidentifiedImageError,
)


class ServerError(HTTPException, LNException):
    def __init__(self, _status=400, *args, **kwargs) -> None:
        self.extra: Optional[str] = None
        super().__init__(_status, *args, **kwargs)

    def with_extra(self, extra: Any) -> "ServerError":
        self.extra = str(extra).strip()
        return self

    def __str__(self) -> str:
        error = f"Error({self.status_code}): {self.detail}"
        if self.extra:
            error += f" [{self.extra}]"
        return error

    def format(self, with_stack=False) -> str:
        stack = ""
        if with_stack:
            lines = traceback.format_exception(
                type(self),
                self,
                self.__traceback__,
                chain=True,
            )
            stack = "".join(lines)
        return f"{self}\n{stack}".strip()

    def to_response(self):
        return JSONResponse(
            status_code=self.status_code,
            headers=self.headers,
            content={
                "error": self.detail,
                "detail": self.extra,
            },
        )


class ServerErrors:
    forbidden = ServerError(status.HTTP_403_FORBIDDEN, "Forbidden")
    not_found = ServerError(status.HTTP_404_NOT_FOUND, "Not Found")
    unauthorized = ServerError(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    rate_limit = ServerError(status.HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests")
    server_error = ServerError(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")
    service_unavailable = ServerError(status.HTTP_503_SERVICE_UNAVAILABLE, "Service Unavailable")

    wrong_otp = ServerError(status.HTTP_403_FORBIDDEN, "Wrong OTP")
    token_invalid = ServerError(status.HTTP_403_FORBIDDEN, "Invalid token")
    token_expired = ServerError(status.HTTP_403_FORBIDDEN, "Token expired")
    inactive_user = ServerError(status.HTTP_403_FORBIDDEN, "User is inactive")
    user_exists = ServerError(status.HTTP_409_CONFLICT, "User already exists")
    email_not_verified = ServerError(status.HTTP_401_UNAUTHORIZED, "Email is not verified")
    email_already_verified = ServerError(status.HTTP_409_CONFLICT, "Email is already verified")
    can_not_delete_self = ServerError(
        status.HTTP_403_FORBIDDEN, "You are not allowed to delete your own account"
    )
    full_novel_not_allowed = ServerError(
        status.HTTP_403_FORBIDDEN, "Full novel is not allowed for this user"
    )
    tier_not_allowed = ServerError(
        status.HTTP_403_FORBIDDEN, "This feature is not available for your tier"
    )
    job_limit_reached = ServerError(
        status.HTTP_429_TOO_MANY_REQUESTS, "Active job limit reached for your tier"
    )
    library_limit_reached = ServerError(
        status.HTTP_429_TOO_MANY_REQUESTS, "Library limit reached for your tier"
    )
    novel_limit_reached = ServerError(
        status.HTTP_429_TOO_MANY_REQUESTS, "Novel limit per library reached for your tier"
    )

    no_such_user = ServerError(status.HTTP_404_NOT_FOUND, "No such user")
    no_such_job = ServerError(status.HTTP_404_NOT_FOUND, "No such job")
    no_such_file = ServerError(status.HTTP_404_NOT_FOUND, "No such file")
    no_such_novel = ServerError(status.HTTP_404_NOT_FOUND, "No such novel")
    no_such_tag = ServerError(status.HTTP_404_NOT_FOUND, "No such tag")
    no_such_library = ServerError(status.HTTP_404_NOT_FOUND, "No such library")
    no_such_secret = ServerError(status.HTTP_404_NOT_FOUND, "No such secret")
    no_such_volume = ServerError(status.HTTP_404_NOT_FOUND, "No such volume")
    no_such_chapter = ServerError(status.HTTP_404_NOT_FOUND, "No such chapter")
    no_such_artifact = ServerError(status.HTTP_404_NOT_FOUND, "No such artifact")
    no_artifact_file = ServerError(status.HTTP_404_NOT_FOUND, "Artifact file not available")
    no_novel_title = ServerError(status.HTTP_404_NOT_FOUND, "Novel has no title")
    no_chapters = ServerError(status.HTTP_404_NOT_FOUND, "No chapters found")
    no_volumes = ServerError(status.HTTP_404_NOT_FOUND, "No volumes found")
    no_images = ServerError(status.HTTP_404_NOT_FOUND, "No images found")
    no_novel_cover = ServerError(status.HTTP_404_NOT_FOUND, "Novel cover is not available")
    no_epub_file = ServerError(status.HTTP_404_NOT_FOUND, "No EPub file found")

    invalid_url = ServerError(status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid URL")
    invalid_input = ServerError(status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid input")
    no_chapters_to_download = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "No chapters to download"
    )
    no_novels_to_download = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "No novels to download"
    )
    no_volumes_to_download = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "No volumes to download"
    )
    no_images_to_download = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "No images to download"
    )
    no_artifacts_to_create = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "No artifacts to create"
    )
    sort_column_is_none = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "No such field to sort by"
    )
    duplicate_output_format = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "Duplicate formats are not allowed"
    )
    invalid_image_response = ServerError(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid image response"
    )

    translation_failure = ServerError(status.HTTP_503_SERVICE_UNAVAILABLE, "Translation Failure")
    unable_to_resume_job = ServerError(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Unable to resume Job"
    )
    smtp_server_unavailable = ServerError(
        status.HTTP_503_SERVICE_UNAVAILABLE, "SMTP server is not available"
    )
    smtp_server_login_fail = ServerError(
        status.HTTP_503_SERVICE_UNAVAILABLE, "Failed to login to SMTP server"
    )
    email_send_failure = ServerError(status.HTTP_503_SERVICE_UNAVAILABLE, "Failed to send email")
    calibre_exe_not_found = ServerError(
        status.HTTP_503_SERVICE_UNAVAILABLE, "No calibre executables"
    )
    acquire_lock = ServerError(status.HTTP_503_SERVICE_UNAVAILABLE, "Failed to acquire lock")
    ebook_convert_error = ServerError(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed running ebook-convert"
    )
    failed_creating_artifact = ServerError(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create artifact"
    )
    format_not_available = ServerError(
        status.HTTP_503_SERVICE_UNAVAILABLE, "The output format is not available"
    )
    host_rejected = ServerError(status.HTTP_502_BAD_GATEWAY, "The requested domain is rejected")
    source_not_loaded = ServerError(status.HTTP_501_NOT_IMPLEMENTED, "Sources are not loaded")
    no_crawler = ServerError(status.HTTP_501_NOT_IMPLEMENTED, "No crawler found for the domain")
    crawler_test_failure = ServerError(status.HTTP_417_EXPECTATION_FAILED, "Crawler test failed")


class WebSocketError(LNException):
    """Raised when a WebSocket LSP session cannot be started or must be closed."""

    def __init__(self, code: int, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason

    def __str__(self) -> str:
        return f"LanguageServerError({self.code}): {self.reason}"


class WebSocketErros:
    lsp_unavailable = WebSocketError(status.WS_1011_INTERNAL_ERROR, "LSP is not available")
    lsp_session_limit = WebSocketError(status.WS_1013_TRY_AGAIN_LATER, "LSP session limit reached")


def get_exception_handlers():
    def server_error_handler(req: Request, err: ServerError):
        return err.to_response()

    def http_exception_handler(req: Request, err: HTTPException):
        logging.error(repr(err), exc_info=True)
        return JSONResponse(
            status_code=err.status_code,
            content={"error": err.detail},
            headers=err.headers,
        )

    def general_exception_handler(req: Request, err: Exception):
        logging.error(repr(err), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"},
        )

    return {
        ServerError: server_error_handler,
        HTTPException: http_exception_handler,
        Exception: general_exception_handler,
    }
