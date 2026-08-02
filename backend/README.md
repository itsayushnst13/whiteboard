# SyncBoard Backend

FastAPI service for SyncBoard. See the [repository root README](../README.md)
for the full project overview, and [docs/adr/0001-foundation-architecture.md](../docs/adr/0001-foundation-architecture.md)
for why this layer is built the way it is.

## Quick start

```bash
python3.13 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

## Auth & boards

Accounts are email/password with stateless JWT access tokens (`bcrypt` for
hashing, `PyJWT` for signing — see `app/core/security.py`). Set a real
`JWT_SECRET_KEY` in `.env` for anything beyond local dev.

- `POST /auth/register`, `POST /auth/login` — return `{ access_token, user }`
- `GET /auth/me` — current user, requires `Authorization: Bearer <token>`
- `GET /boards`, `POST /boards`, `GET /boards/{id}`, `DELETE /boards/{id}` —
  boards are scoped to their owner; each board carries a `room_id` that the
  frontend hands to Liveblocks to join the real-time room

## Layout

| Directory       | Responsibility                                              |
| --------------- | ------------------------------------------------------------ |
| `api/routes`    | Thin HTTP handlers — parse request, call a service, respond |
| `core`          | App factory, middleware registration, lifespan              |
| `config`        | Typed, validated settings                                   |
| `db`            | Postgres (SQLAlchemy async) and Redis client setup           |
| `dependencies`  | FastAPI `Depends` providers                                  |
| `middleware`    | Request context, structured logging, security headers        |
| `models`        | SQLAlchemy declarative models (`User`, `Board`)               |
| `repositories`  | Generic + domain data-access classes                         |
| `schemas`       | Pydantic request/response models                             |
| `services`      | Business logic, orchestrates repositories                    |
| `exceptions`    | App exception hierarchy + global handlers                    |
| `logging`       | Structured (JSON in prod) logging configuration               |
| `health`        | Low-level dependency check functions                          |
| `tests`         | pytest suite                                                  |

Run `make backend-test`, `make backend-lint`, or `make backend-format` from
the repo root — see the root [Makefile](../Makefile).
