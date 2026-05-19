from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    NotFoundError,
    AlreadyExistsError,
    AuthError,
    PermissionDeniedError,
    ValidationError
)

ERROR_STATUS_MAP = {
    NotFoundError: 404,
    AlreadyExistsError: 409,
    AuthError: 401,
    PermissionDeniedError: 403,
    ValidationError: 400,
}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_code = ERROR_STATUS_MAP.get(type(exc), 500)
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )