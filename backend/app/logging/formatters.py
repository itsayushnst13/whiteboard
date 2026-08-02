import json
import logging
from datetime import UTC, datetime
from typing import Any, ClassVar


class JsonFormatter(logging.Formatter):
    """Renders each log record as one JSON object per line, so logs are
    directly queryable in any log aggregator (CloudWatch, Datadog, Loki)
    without a separate parsing stage."""

    _RESERVED: ClassVar[frozenset[str]] = frozenset(
        logging.LogRecord("", 0, "", 0, "", (), None).__dict__
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extras = {key: value for key, value in record.__dict__.items() if key not in self._RESERVED}
        payload.update(extras)

        return json.dumps(payload, default=str)
