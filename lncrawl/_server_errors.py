"""Server-only error types that depend on FastAPI.

Split out of :mod:`lncrawl.exceptions` so that importing the crawler-level
exceptions (``LNException``, ``ScraperErrorGroup`` …) on the CLI path does not
drag in FastAPI. These names remain importable from ``lncrawl.exceptions`` via
its module-level ``__getattr__``; the server imports FastAPI regardless.
"""

import logging
import traceback
from typing import Any, Callable, Generic, Optional, TypeVar

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from .exceptions import LNException

E = TypeVar("E", bound=BaseException)


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


class _E(Generic[E]):
    __slots__ = ("_factory", "_args")

    def __init__(self, factory: Callable[..., E], *args: Any) -> None:
        self._factory = factory
        self._args = args

    def __get__(self, obj: Any, objtype: Any = None) -> E:
        return self._factory(*self._args)


def _se(*args: Any):
    return _E(ServerError, *args)


class ServerErrors:
    forbidden = _se(
        status.HTTP_403_FORBIDDEN,
        "Forbidden",
    )
    not_found = _se(
        status.HTTP_404_NOT_FOUND,
        "Not Found",
    )
    unauthorized = _se(
        status.HTTP_401_UNAUTHORIZED,
        "Unauthorized",
    )
    rate_limit = _se(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Too Many Requests",
    )
    server_error = _se(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Internal Server Error",
    )
    service_unavailable = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Service Unavailable",
    )

    wrong_otp = _se(
        status.HTTP_403_FORBIDDEN,
        "Wrong OTP",
    )
    token_invalid = _se(
        status.HTTP_403_FORBIDDEN,
        "Invalid token",
    )
    token_expired = _se(
        status.HTTP_403_FORBIDDEN,
        "Token expired",
    )
    inactive_user = _se(
        status.HTTP_403_FORBIDDEN,
        "User is inactive",
    )
    user_exists = _se(
        status.HTTP_409_CONFLICT,
        "User already exists",
    )
    email_not_verified = _se(
        status.HTTP_401_UNAUTHORIZED,
        "Email is not verified",
    )
    email_already_verified = _se(
        status.HTTP_409_CONFLICT,
        "Email is already verified",
    )
    can_not_delete_self = _se(
        status.HTTP_403_FORBIDDEN,
        "You are not allowed to delete your own account",
    )
    full_novel_not_allowed = _se(
        status.HTTP_403_FORBIDDEN,
        "Full novel is not allowed for this user",
    )
    tier_not_allowed = _se(
        status.HTTP_403_FORBIDDEN,
        "This feature is not available for your tier",
    )
    translation_disabled = _se(
        status.HTTP_403_FORBIDDEN,
        "Translation is currently disabled",
    )
    job_limit_reached = _se(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Active job limit reached for your tier",
    )
    search_job_limit_reached = _se(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Search job limit reached for your tier",
    )
    library_limit_reached = _se(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Library limit reached for your tier",
    )
    novel_limit_reached = _se(
        ServerError,
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Novel limit per library reached for your tier",
    )

    no_such_user = _se(
        status.HTTP_404_NOT_FOUND,
        "No such user",
    )
    no_such_job = _se(
        status.HTTP_404_NOT_FOUND,
        "No such job",
    )
    no_such_file = _se(
        status.HTTP_404_NOT_FOUND,
        "No such file",
    )
    no_such_novel = _se(
        status.HTTP_404_NOT_FOUND,
        "No such novel",
    )
    no_such_tag = _se(
        status.HTTP_404_NOT_FOUND,
        "No such tag",
    )
    no_such_library = _se(
        status.HTTP_404_NOT_FOUND,
        "No such library",
    )
    no_such_secret = _se(
        status.HTTP_404_NOT_FOUND,
        "No such secret",
    )
    no_such_volume = _se(
        status.HTTP_404_NOT_FOUND,
        "No such volume",
    )
    no_such_chapter = _se(
        status.HTTP_404_NOT_FOUND,
        "No such chapter",
    )
    no_such_artifact = _se(
        status.HTTP_404_NOT_FOUND,
        "No such artifact",
    )
    no_artifact_file = _se(
        status.HTTP_404_NOT_FOUND,
        "Artifact file not available",
    )
    no_novel_title = _se(
        status.HTTP_404_NOT_FOUND,
        "Novel has no title",
    )
    no_chapters = _se(
        status.HTTP_404_NOT_FOUND,
        "No chapters found",
    )
    no_volumes = _se(
        status.HTTP_404_NOT_FOUND,
        "No volumes found",
    )
    no_images = _se(
        status.HTTP_404_NOT_FOUND,
        "No images found",
    )
    no_novel_cover = _se(
        status.HTTP_404_NOT_FOUND,
        "Novel cover is not available",
    )
    no_epub_file = _se(
        status.HTTP_404_NOT_FOUND,
        "No EPub file found",
    )

    invalid_url = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Invalid URL",
    )
    invalid_input = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Invalid input",
    )
    no_chapters_to_download = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "No chapters to download",
    )
    no_novels_to_download = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "No novels to download",
    )
    no_volumes_to_download = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "No volumes to download",
    )
    no_images_to_download = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "No images to download",
    )
    no_artifacts_to_create = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "No artifacts to create",
    )
    sort_column_is_none = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "No such field to sort by",
    )
    duplicate_output_format = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Duplicate formats are not allowed",
    )
    invalid_image_response = _se(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Invalid image response",
    )

    translation_failure = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Translation Failure",
    )
    translation_service_unavailable = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Translator service is not reachable",
    )
    translation_quota_exhausted = _se(
        ServerError,
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "All translation engines are quota-exhausted",
    )
    unable_to_resume_job = _se(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Unable to resume Job",
    )
    smtp_server_unavailable = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "SMTP server is not available",
    )
    smtp_server_login_fail = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Failed to login to SMTP server",
    )
    imap_server_unavailable = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "IMAP server is not available",
    )
    imap_server_login_fail = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Failed to login to IMAP server",
    )
    email_send_failure = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Failed to send email",
    )
    calibre_exe_not_found = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "No calibre executables",
    )
    acquire_lock = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Failed to acquire lock",
    )
    ebook_convert_error = _se(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Failed running ebook-convert",
    )
    failed_creating_artifact = _se(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Failed to create artifact",
    )
    format_not_available = _se(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "The output format is not available",
    )
    host_rejected = _se(
        status.HTTP_502_BAD_GATEWAY,
        "The requested domain is rejected",
    )
    source_not_loaded = _se(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Sources are not loaded",
    )
    no_crawler = _se(
        status.HTTP_501_NOT_IMPLEMENTED,
        "No crawler found for the domain",
    )
    crawler_test_failure = _se(
        status.HTTP_417_EXPECTATION_FAILED,
        "Crawler test failed",
    )
    search_not_supported = _se(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Search is not implemented for the source",
    )


class WebSocketError(LNException):
    """Raised when a WebSocket LSP session cannot be started or must be closed."""

    def __init__(self, code: int, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason

    def __str__(self) -> str:
        return f"LanguageServerError({self.code}): {self.reason}"


class WebSocketErros:
    lsp_unavailable = _E(
        WebSocketError,
        status.WS_1011_INTERNAL_ERROR,
        "LSP is not available",
    )
    lsp_session_limit = _E(
        WebSocketError,
        status.WS_1013_TRY_AGAIN_LATER,
        "LSP session limit reached",
    )


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
