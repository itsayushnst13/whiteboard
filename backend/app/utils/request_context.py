from fastapi import Request

REQUEST_ID_HEADER = "X-Request-ID"


def get_request_id(request: Request) -> str:
    """Read the request ID that `RequestContextMiddleware` attaches to
    every request. Falls back to "unknown" only for requests that never
    passed through the middleware (e.g. exceptions raised before it runs)."""
    return getattr(request.state, "request_id", "unknown")
