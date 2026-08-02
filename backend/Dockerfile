# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# README.md is required at build time, not just for docs: pyproject.toml
# points `readme` at it and hatchling errors out if it's missing.
COPY pyproject.toml alembic.ini README.md ./
COPY app ./app
COPY alembic ./alembic
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh


FROM base AS development

RUN pip install --upgrade pip && pip install -e ".[dev]"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM base AS production

RUN pip install --upgrade pip && pip install .

RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail "http://localhost:${PORT:-8000}/liveness" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
