# SyncBoard Frontend

Vite + React + TypeScript client for SyncBoard — a real-time collaborative
whiteboard (draw, shapes, text, sticky notes, undo/redo, export to PNG),
with accounts and saved boards. See the [repository root](../README.md)
for the full project overview.

## Quick start

```bash
npm install
cp .env.example .env
# then add a Liveblocks public key to .env, see below
npm run dev
```

Open `http://localhost:5173`. Sign up or log in, then create a board from
the dashboard — each board gets its own room that others can join live.

## Routes

| Route               | Page                                                                    |
| -------------------- | ------------------------------------------------------------------------ |
| `/login`            | Log in                                                                   |
| `/register`         | Create an account                                                        |
| `/boards`           | Dashboard — "Owned boards" and "Shared with me", create/rename/delete    |
| `/board/:boardId`   | The whiteboard itself (protected — redirects to `/login`)                |

`/board/:boardId` is the permanent, shareable URL for a board (numeric
board id, not the Liveblocks room token). On load it calls
`GET /boards/:boardId` and branches on the result: 200 opens the board with
the caller's `role` (owner/editor/viewer), 403 shows "You don't have access
to this board" (no silent redirect), 404 shows "This board doesn't exist".
See `App.tsx`'s `BoardRoute`.

## Sharing & roles

The top bar's **Share** button opens a dialog to copy the board's link,
invite a collaborator by email (owner only — picks a role of Editor or
Viewer), and manage/remove existing collaborators. A `viewer` sees a
"View only" badge and gets a read-only canvas (`Board.tsx`'s `readOnly`
prop disables the toolbar and all draw/erase/move/undo/redo handlers).
See `backend/README.md` for the full permission matrix and API, and for an
important caveat: this gates the REST API, not the Liveblocks room itself
(see below).

Auth state lives in `features/auth/lib/AuthContext.tsx`: a JWT from the
backend is stored in `localStorage` and attached to API requests by
`lib/api.ts`. `features/auth/components/ProtectedRoute.tsx` gates the
dashboard and board routes.

## Real-time sync (Liveblocks)

Multiplayer sync, cursors, and undo/redo run on
[Liveblocks](https://liveblocks.io). Get a free public API key:

1. Sign up at https://liveblocks.io/dashboard and create a project.
2. Copy the `pk_dev_...` (or `pk_prod_...`) public key from **API keys**.
3. Put it in `frontend/.env` as `VITE_LIVEBLOCKS_PUBLIC_KEY=pk_...`.

Without a key, the app still loads but shows "Connecting to board…"
indefinitely — the console will log a reminder, and the toolbar disables
itself (grayed out) until the room actually connects, so a missing/invalid
key can't be used to trigger a crash from an unloaded-storage mutation.

**Why a public key instead of a backend auth endpoint:** Liveblocks'
secure, permission-checked auth flow is only exposed as a documented
integration through the `@liveblocks/node` SDK (Node-only). SyncBoard's
backend is Python/FastAPI, and the raw REST contract that SDK wraps isn't
publicly documented, so reverse-engineering it risked a subtly broken auth
flow. The public-key mode is officially supported for this exact case and
is what SyncBoard uses today. If per-room/per-user permissions are needed
later, add a small Node microservice (or Next.js API route) that calls
`@liveblocks/node`'s `prepareSession(...).authorize()` and switch the
client to `createClient({ authEndpoint: ... })` in
`src/features/whiteboard/lib/liveblocks.ts`.

Practical effect on the sharing feature above: anyone who knows a board's
`room_id` (not exposed in the URL, but visible to anyone the backend has
already granted access to) can technically join that Liveblocks room from
a raw client, since public-key mode doesn't check per-room permissions
server-side. The REST API's owner/editor/viewer checks are real; the
"viewer can't edit" restriction on the canvas itself is enforced in the
frontend UI, not cryptographically. This is the same tradeoff called out
above, just applied to roles instead of room access generally.

## Layout

| Directory                        | Responsibility                                   |
| --------------------------------- | ------------------------------------------------- |
| `features/auth`                  | Login/register pages, AuthContext, ProtectedRoute |
| `features/boards`                | Boards dashboard, collaborator API helpers        |
| `features/whiteboard/components` | Canvas, toolbar, top bar, share dialog, cursors    |
| `features/whiteboard/lib`        | Liveblocks client/room config, identity, geometry |
| `features/whiteboard/types`      | Shape/tool type definitions                       |
| `lib/api.ts`                     | Fetch wrapper: base URL, JWT header, error envelope |

Run `make frontend-test`, `make frontend-lint`, or `make frontend-format`
from the repo root — see the root [Makefile](../Makefile).
