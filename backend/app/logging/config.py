import logging
import sys

from app.config import Settings
from app.logging.formatters import JsonFormatter


def setup_logging(settings: Settings) -> None:
    """Configure the root logger once at startup. Plain text in
    development (readable in a terminal), structured JSON everywhere else
    (parseable by log aggregators)."""
    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL)
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if settings.is_production:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )

    root.addHandler(handler)

    # Quiet noisy third-party loggers unless we're actively debugging.
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy_logger).setLevel(
            logging.WARNING if not settings.DEBUG else logging.INFO
        )
