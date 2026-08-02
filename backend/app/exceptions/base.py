class AppException(Exception):
    """Base class for exceptions that should be translated into a
    consistent `ApiResponse` error envelope rather than an unhandled 500.

    Raise a subclass (or this directly) from services/repositories; route
    handlers never need their own try/except for these.
    """

    def __init__(self, message: str, *, code: str = "APP_ERROR", status_code: int = 500) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="NOT_FOUND", status_code=404)


class ServiceUnavailableError(AppException):
    def __init__(self, message: str = "Service temporarily unavailable") -> None:
        super().__init__(message, code="SERVICE_UNAVAILABLE", status_code=503)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message, code="CONFLICT", status_code=409)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message, code="UNAUTHORIZED", status_code=401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "You don't have permission to do this") -> None:
        super().__init__(message, code="FORBIDDEN", status_code=403)
