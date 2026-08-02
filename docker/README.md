# docker/

Shared Docker assets that don't belong to a single app (database init
scripts, reverse-proxy config, seed data volumes).

`frontend/Dockerfile` and `backend/Dockerfile` live next to the code they
build — that keeps each build context minimal and lets each app own its own
image. This directory is for infrastructure that's shared across services.

Nothing lives here yet because the foundation milestone only needs the
official `postgres` and `redis` images as-is (see `docker-compose.yml`). It
will start holding real files as soon as a service needs one, for example:

- `docker/postgres/initdb/` — SQL/shell scripts run on first container start
- `docker/nginx/` — reverse-proxy config for serving the built frontend in production
