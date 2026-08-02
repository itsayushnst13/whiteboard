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
- `GET /boards`, `POST /boards`, `GET /boards/{id}`, `PATCH /boards/{id}`,
  `DELETE /boards/{id}` — each board carries a `room_id` that the frontend
  hands to Liveblocks to join the real-time room, and a `role` (see below)
  telling the caller what they're allowed to do with it

## Sharing & permissions

Every board has exactly one **owner** (`Board.owner_id`) plus any number of
**collaborators** (`board_collaborators` table), each with a role:

| Role      | Rename / delete board | Invite / remove collaborators | Draw / edit / erase / undo / redo / export | View |
| --------- | :--------------------: | :----------------------------: | :-----------------------------------------: | :--: |
| `owner`   | ✅ | ✅ | ✅ | ✅ |
| `editor`  | ❌ | ❌ | ✅ | ✅ |
| `viewer`  | ❌ | ❌ | ❌ | ✅ |

- `POST /boards/{id}/share`, `POST /boards/{id}/collaborators` — invite (or
  re-invite to change the role of) a collaborator by email. Owner only.
  404 if no account exists with that email, 409 if it's the owner's own
  email, otherwise upserts the `board_collaborators` row.
- `GET /boards/{id}/collaborators` — list collaborators. Owner or any
  collaborator can view it.
- `DELETE /boards/{id}/collaborators/{userId}` — remove a collaborator.
  Owner only.
- `GET /boards/{id}` — **404** if the board id doesn't exist at all,
  **403** if it exists but the caller is neither owner nor collaborator,
  **200** with the caller's `role` otherwise. The 403/404 split is
  intentional (see `app/services/board_service.py::_get_board_and_role`)
  so the frontend can show "you don't have access" instead of silently
  pretending the board never existed.

**Known limitation:** these checks gate the REST API (who can see/rename/
delete/invite on a board) but do **not** gate the Liveblocks room itself —
see `frontend/README.md` for why the client uses Liveblocks' public-key
mode rather than a permissioned/authenticated room. In practice this means
a `viewer`'s browser is trusted (via the frontend UI) not to send draw
mutations, rather than being cryptographically prevented from doing so.
Closing that gap fully would require switching to Liveblocks' secret-key
auth flow, which was deliberately deferred — see that README for the
tradeoff.

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
