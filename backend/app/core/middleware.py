from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.middleware import RequestContextMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """Registration order matters: the middleware added last runs first
    on the way in, so CORS wraps everything (it must handle preflight
    requests before any other middleware sees them), and request-ID
    assignment happens before the logging middleware needs it."""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
