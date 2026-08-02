import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.base import AppException
from app.schemas.response import ApiResponse, ErrorDetail
from app.utils.request_context import get_request_id

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = get_request_id(request)
    envelope = ApiResponse[None].fail(
        ErrorDetail(code=exc.code, message=exc.message), request_id=request_id
    )
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump(mode="json"))


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = get_request_id(request)
    envelope = ApiResponse[None].fail(
        ErrorDetail(code="HTTP_ERROR", message=str(exc.detail)), request_id=request_id
    )
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump(mode="json"))


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = get_request_id(request)
    details = [
        {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
        for error in exc.errors()
    ]
    envelope = ApiResponse[None].fail(
        ErrorDetail(code="VALIDATION_ERROR", message="Request validation failed", details=details),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=envelope.model_dump(mode="json"),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    logger.exception(
        "Unhandled exception while processing request", extra={"request_id": request_id}
    )
    envelope = ApiResponse[None].fail(
        ErrorDetail(code="INTERNAL_ERROR", message="An unexpected error occurred"),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=envelope.model_dump(mode="json"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    # Starlette's `add_exception_handler` is typed to accept a handler for
    # the base `Exception`, but each of ours is (correctly, and more
    # usefully) narrowed to the specific exception type it's registered
    # for — FastAPI's own documented pattern for this hits the same mypy
    # --strict friction.
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        StarletteHTTPException, http_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, unhandled_exception_handler)
