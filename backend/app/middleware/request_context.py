import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.utils.request_context import REQUEST_ID_HEADER


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attaches a request ID to every request — reused from the incoming
    header when a client (or upstream proxy) already set one, otherwise
    generated fresh — so it can be correlated across logs and the
    response's `X-Request-ID` header."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
