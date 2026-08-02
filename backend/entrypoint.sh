#!/bin/sh
# Production container entrypoint: apply any pending Alembic migrations
# before the app starts serving traffic, then hand off to uvicorn.
#
# Binds to $PORT rather than a hardcoded port — Railway (and most PaaS
# hosts) assign a container's external port via that env var at runtime,
# and a hardcoded --port would silently not match what the platform
# routes traffic to. Falls back to 8000 for plain `docker run`/Compose.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-4}"
