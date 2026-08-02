# SyncBoard

A real-time collaborative whiteboard: draw, add shapes and text, drop
sticky notes, undo/redo together, and export the board as an image —
all synced live across everyone in the room.

## Stack

- **Frontend** — Vite + React + TypeScript + Tailwind CSS, canvas via
  [Konva](https://konvajs.org)/`react-konva`, real-time sync via
  [Liveblocks](https://liveblocks.io).
- **Backend** — FastAPI (Python 3.13), Postgres, Redis.

See [`frontend/README.md`](frontend/README.md) and
[`backend/README.md`](backend/README.md) for service-specific setup, and
[`DEPLOYMENT.md`](DEPLOYMENT.md) for deploying to Vercel + Railway + Neon.

## Quick start

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# add a Liveblocks public key to frontend/.env — see frontend/README.md

make install   # backend venv + frontend node_modules
make dev       # starts Postgres + Redis in Docker
make backend-dev    # in one terminal
make frontend-dev   # in another
```

Or run everything in Docker: `make up`.

Open `http://localhost:5173`. Sign up, create a board from the dashboard,
and share its URL with others to collaborate on it live.

## Features

- Email/password accounts — boards are saved per user and listed on a
  dashboard after login, split into "Owned boards" and "Shared with me"
- Board sharing with owner/editor/viewer roles — invite a collaborator by
  email from the Share dialog, copy a permanent board link, remove access
- Freehand draw and erase
- Rectangle, ellipse, star, line, and arrow shapes
- Text and sticky notes
- Real-time multiplayer cursors and shared undo/redo
- Export the board as a PNG
- Zoom and pan

## Status

The whiteboard app, accounts, saved boards, and sharing/permissions are
built and working. AI features are planned as a follow-up phase.

Backend and frontend test suites are green, and CI runs lint, typecheck,
tests, and a production build on every push — see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml). For deployment, see
[`DEPLOYMENT.md`](DEPLOYMENT.md).
