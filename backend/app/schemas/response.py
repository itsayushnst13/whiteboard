from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ApiResponse(BaseModel, Generic[T]):
    """The single response envelope every endpoint in the API returns,
    success or failure, so clients only need one parsing path."""

    success: bool
    data: T | None = None
    error: ErrorDetail | None = None
    meta: ResponseMeta

    @classmethod
    def ok(cls, data: T, request_id: str) -> "ApiResponse[T]":
        return cls(success=True, data=data, error=None, meta=ResponseMeta(request_id=request_id))

    @classmethod
    def fail(cls, error: ErrorDetail, request_id: str) -> "ApiResponse[T]":
        return cls(success=False, data=None, error=error, meta=ResponseMeta(request_id=request_id))
