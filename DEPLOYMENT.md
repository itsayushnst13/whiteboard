# Deploying SyncBoard

This covers deploying the frontend to **Vercel**, the backend to **Railway**,
and the database to **Neon**. Everything code-level (Dockerfiles, migration
normalization, CI, platform config files) is already done — see "What's
already fixed" below. The steps in this doc are the ones only you can do:
they require logging into three external dashboards, which this environment
has no network access to (verified directly — DNS doesn't even resolve
`vercel.com`, `railway.app`, or `neon.tech` from here).

Each step says **why**, exactly **what to click**, and what to do **after**.

## What's already fixed in the repo

- **`app/db/url.py`** — Neon (and most managed Postgres) hand out
  `postgres://...?sslmode=require` connection strings. SQLAlchemy's asyncpg
  driver passes every query param straight through as a Python keyword
  argument rather than parsing it as a libpq DSN, and `asyncpg.connect()`
  has no `sslmode` parameter — only `ssl`. Verified directly: passing
  `sslmode="require"` raises `TypeError: connect() got an unexpected keyword
  argument 'sslmode'`; `ssl=True` does not. This was a real, guaranteed
  crash-on-first-query bug against Neon. Fixed by normalizing the URL
  (scheme → `postgresql+asyncpg://`, `sslmode`/`channel_binding` stripped
  and translated to `connect_args={"ssl": True}`), used by both the app's
  engine and Alembic — see `backend/app/tests/unit/test_database_url.py`
  for the test coverage.
- **`backend/entrypoint.sh` + `Dockerfile`** — production container now
  runs `alembic upgrade head` before starting uvicorn, and binds to `$PORT`
  (Railway assigns this dynamically; the old Dockerfile hardcoded `8000`,
  which would silently not match Railway's routing).
- **`railway.json`** (repo root) — sets a pre-deploy `alembic upgrade head`
  step (Railway's officially recommended way to run migrations: once per
  deploy, before any replica starts, rather than racing across replicas),
  the `/liveness` healthcheck, and a restart policy.
- **`vercel.json`** (repo root) — monorepo-aware build (`cd frontend && npm
  run build`), and a SPA rewrite so refreshing `/board/:id` or `/login`
  doesn't 404.
- **`.github/workflows/ci.yml`** — lints, typechecks, tests, and builds both
  backend and frontend on every push/PR to `main`. Confirmed working: 47/48
  backend tests pass (1 pre-existing unrelated failure, see root README),
  17/17 frontend tests pass, `tsc -b` and `vite build` both clean.
- Everything else (CORS via env var, required `JWT_SECRET_KEY` with no
  insecure default, `/health` `/liveness` `/readiness` endpoints, security
  headers, non-root Docker user) was already production-appropriate.

Deploy-on-push happens natively once Vercel/Railway are connected to the
GitHub repo (their own GitHub App integration) — no Actions deploy step is
needed for that part.

---

## 1. Neon (database)

**Why:** Postgres needs to exist before the backend can start.

1. Go to https://console.neon.tech and sign in / create an account.
2. Click **New Project**. Name it `syncboard`, pick a region close to
   wherever you'll host Railway (e.g. same AWS region).
3. On the project's **Dashboard**, copy the **Connection string** shown
   under "Connection Details" — pick the **Pooled connection** variant if
   offered (better for a web backend's connection pattern). It looks like:
   ```
   postgresql://neondb_owner:xxxxx@ep-xxxxx-pooler.region.aws.neon.tech/neondb?sslmode=require
   ```
4. Save that string — you'll paste it into Railway as `DATABASE_URL` in
   step 2. Nothing else needed here; the app's own `alembic upgrade head`
   (run automatically via Railway's pre-deploy step) creates all tables
   (`users`, `boards`, `board_collaborators`) on first deploy.

*(Continue automatically once you've copied the connection string.)*

---

## 2. Railway (backend)

**Why:** Runs the FastAPI container.

1. Go to https://railway.com and sign in with GitHub (this also grants
   Railway access to your repos).
2. **New Project** → **Deploy from GitHub repo** → pick this repo.
3. Railway creates one service from the repo root. Open its **Settings**
   tab:
   - **Root Directory**: set to `backend` (this repo is a monorepo — this
     tells Railway the Dockerfile, and everything the Dockerfile `COPY`s,
     live under `backend/`, not the repo root).
   - Leave **Builder** on its default; Railway auto-detects the
     `Dockerfile` once Root Directory is set and always prefers a
     Dockerfile over Railpack when one is present.
4. Add a **Redis** database: in the project canvas, **+ New** → **Database**
   → **Add Redis**. (Currently only used by the `/readiness` check, not
   anything user-facing, but `REDIS_URL` is a required setting and the app
   won't start without it.)
5. On the backend service's **Variables** tab, add:
   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | the Neon connection string from step 1 |
   | `REDIS_URL` | `${{Redis.REDIS_URL}}` (Railway's reference-variable syntax — autofills from the Redis service you just added) |
   | `JWT_SECRET_KEY` | a real random secret — generate one with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` and paste the output |
   | `BACKEND_CORS_ORIGINS` | leave a placeholder for now (e.g. `https://placeholder.vercel.app`) — you'll update this in step 4 once the real Vercel URL exists |
   | `ENVIRONMENT` | `production` |
   | `DEBUG` | `false` |

   Do **not** set `PORT` — Railway injects it automatically and the
   container reads it via `entrypoint.sh`.
6. Deploy (Railway does this automatically after variables are saved, or
   click **Deploy**). Watch the build logs for `Using detected
   Dockerfile!`, then `Running database migrations...`, then
   `Running upgrade -> ... create board_collaborators table`, then
   `Starting uvicorn on port ...`.
7. Once deployed, **Settings → Networking → Generate Domain** to get a
   public URL, e.g. `https://syncboard-backend-production.up.railway.app`.

*(Continue automatically once you have this URL — paste it back to me and
I'll verify `/health` and `/liveness` respond, and sanity-check the
response shape.)*

---

## 3. Vercel (frontend)

**Why:** Serves the built React app.

1. Go to https://vercel.com and sign in with GitHub.
2. **Add New** → **Project** → import this repo.
3. Vercel should detect `vercel.json` at the repo root and use its
   `buildCommand`/`installCommand`/`outputDirectory` automatically (all
   prefixed with `cd frontend &&`, so you do **not** need to change
   Vercel's "Root Directory" project setting — leave it at `/`).
4. Under **Environment Variables**, add:
   | Variable | Value |
   |---|---|
   | `VITE_API_BASE_URL` | the Railway URL from step 2 |
   | `VITE_LIVEBLOCKS_PUBLIC_KEY` | a **production** key (`pk_prod_...`) from https://liveblocks.io/dashboard/apikeys — create a Liveblocks project if you haven't (separate free account, same idea as Neon/Railway) |
5. Click **Deploy**. You'll get a URL like `https://syncboard.vercel.app`.

*(Continue automatically once you have this URL.)*

---

## 4. Close the loop: real CORS origin

**Why:** Right now the backend's `BACKEND_CORS_ORIGINS` is still the
placeholder from step 2 — the browser will block every API request from
your real Vercel domain until this is fixed.

1. Back in Railway, backend service **Variables**, set:
   ```
   BACKEND_CORS_ORIGINS=https://your-real-app.vercel.app
   ```
   (comma-separate multiple origins if you also want e.g. a
   `*.vercel.app` preview URL — Vercel gives every deploy a unique preview
   URL in addition to the production domain).
2. Save — Railway redeploys automatically.

*(Continue automatically once saved — tell me both final URLs and I'll run
through the verification checklist below against them.)*

---

## After you've done the above

Tell me the two URLs (Vercel frontend, Railway backend) and I will:

- Fetch `/health` and `/liveness` on the backend directly and confirm they
  respond correctly.
- Load the frontend and confirm it renders and reaches the backend
  (whatever I can check without a live browser session — for anything
  requiring an actual signed-in browser, like drawing/undo/redo/two-user
  collaboration, I'll need you to do a quick pass yourself and report back,
  since I don't have a browser connected to your machine in this session).

I'll keep iterating on any errors you paste back from Railway/Vercel build
logs or the browser console — I just can't click through the dashboards
myself from here.
