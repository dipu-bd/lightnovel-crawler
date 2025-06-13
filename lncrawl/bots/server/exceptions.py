import traceback

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from .app import app


class AppError(HTTPException):
    def __init__(self, status=400, *args, **kwargs) -> None:
        super().__init__(status, *args, **kwargs)


class AppErrors:
    forbidden = AppError(403, 'Forbidden')
    not_found = AppError(404, 'Not Found')
    unauthorized = AppError(401, 'Unauthorized')
    server_error = AppError(500, 'Internal Server Error')

    sort_column_is_none = AppError(422, "No such field to sort by")

    no_such_user = AppError(404, "No such user")
    inactive_user = AppError(403, 'User is inactive')
    user_exists = AppError(409, "User already exists")
    can_not_delete_self = AppError(403, 'You are not allowed to delete your own account')

    no_such_job = AppError(404, "No such job")
    duplicate_output_format = AppError(422, "Duplicate formats are not allowed")

    no_such_novel = AppError(404, "No such novel")
    no_such_artifact = AppError(404, "No such artifact")
    no_artifact_file = AppError(404, "Artifact file not available")
    email_already_verified = AppError(409, "Email is already verified")

    no_novel_title = AppError(500, "Novel has no title")
    unable_to_resume_job = AppError(500, "Unable to resume Job")
    no_novel_cover = AppError(500, "Novel cover is not available")
    invalid_image_response = AppError(500, "Invalid image response")
    smtp_server_unavailable = AppError(500, "SMTP server is not available")
    email_send_failure = AppError(500, "Failed to send email")
    no_novel_output_path = AppError(500, "Novel output path is not found")
    malformed_json_file = AppError(500, 'Malformed JSON file')
    no_metadata_file = AppError(500, "Novel metadata file is not found")
    malformed_metadata_file = AppError(500, "Novel metadata file is malformed")


@app.exception_handler(AppError)
async def global_client_error_handler(req: Request, err: AppError):
    return JSONResponse(
        status_code=err.status_code,
        content={"detail": err.detail},
        headers=err.headers,
    )


@app.exception_handler(HTTPException)
async def global_http_exception_handler(req: Request, err: HTTPException):
    traceback.print_exception(err)
    return JSONResponse(
        status_code=err.status_code,
        content={"detail": err.detail},
        headers=err.headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(req: Request, err: Exception):
    traceback.print_exception(err)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
