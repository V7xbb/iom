# HKRROE — CYBER NEO v3

A bilingual Arabic-first developer identity site with a real FastAPI backend, PostgreSQL/SQLite storage, an admin console, social-link management, project and news publishing, internal verification records, visit counts, and live service health checks.

## Architecture

- `frontend/`: Next.js App Router, TypeScript, responsive RTL interface, animated 3D-style social cubes, mascot artwork, QR-linked digital identity, and admin dashboard.
- `backend/`: FastAPI, SQLAlchemy, password hashing, signed expiring bearer tokens, admin-only CRUD endpoints, health checks, and activity records.
- `backend/migrations/`: Alembic migration setup.
- `docs/design-reference.png`: approved visual reference used to guide the implementation.

## Local development

Requirements: Python 3.11+, Node.js 20+, and npm. PostgreSQL is recommended; SQLite is supported for a local smoke run.

1. Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # set variables in your shell or load them with your preferred dotenv runner
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

2. Frontend, in another terminal:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`; API docs are at `http://localhost:8000/docs`.

## First admin account

Set these backend environment variables before the API's first startup:

- `ADMIN_USERNAME`: chosen admin username.
- `ADMIN_PASSWORD`: unique password of at least 12 characters.
- `JWT_SECRET_KEY`: random secret of at least 32 characters.
- `VISITOR_HASH_SECRET`: separate random secret used to hash daily visitor keys.

The first startup creates the admin user once. It does not expose a public admin-registration endpoint. You can change the password from the admin console after signing in. Keep the JWT secret private; changing it invalidates active sessions.

## Render deployment

1. Push this folder as a Git repository.
2. In Render choose **New → Blueprint** and select that repository.
3. Before applying the Blueprint, provide `ADMIN_USERNAME` and `ADMIN_PASSWORD` when Render requests them.
4. Render provisions the API, Next.js frontend, and PostgreSQL database from `render.yaml`.
5. After deployment, open the frontend `/dashboard` route and sign in with the bootstrap admin credentials.

Render free services may sleep or have other plan limits. Persistent database storage and current plan details should be checked in the Render dashboard before public launch.

## Admin console

`/dashboard` supports:

- Overview counts.
- Create, edit, publish/unpublish, feature, and delete projects.
- Create, edit, publish/unpublish, and delete news posts.
- Approve, mark pending, or revoke HKRROE internal verification records.
- Update Telegram, WhatsApp, Instagram, TikTok, YouTube, and Discord links.
- Change the admin password.

All write endpoints require a valid admin bearer token. Public endpoints are read-only except for page-visit recording and verification requests.

## API summary

- `GET /api/health`, `GET /api/stats`, `POST /api/visits`
- `GET /api/projects`, `GET /api/news`, `GET /api/activity`, `GET /api/settings`
- `POST /api/verified`, `GET /api/verified/{public_id}`
- `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/change-password`
- Admin CRUD under `/api/admin/projects`, `/api/admin/news`, `/api/admin/verifications`, `/api/admin/settings`

## Truthful operating notes

- The command center displays health checks and database connectivity returned by the backend. Uptime is process uptime, not a promised 99.9% service-level guarantee.
- Visitor statistics count unique hashed IP/day pairs. Raw IP addresses are not stored in the visits table. Behind a proxy, configure trusted proxy behavior carefully before treating visitor counts as analytics-grade.
- Discord username `rtx_vipq` is displayed with a copy action because a Discord username by itself is not a server invite URL or a guaranteed public profile URL.
- HKRROE Verified is an internal site feature, not official verification by Telegram, Instagram, or another external platform.
- Project/news image fields currently accept secure `http(s)` URLs; local media upload management is not included in this version.
- A deployment still needs your own domain (optional), environment variables, and a successful live deployment check. This archive does not publish the site by itself.

## Production checklist

- Set a unique strong admin password and generated random secrets.
- Use HTTPS and a restricted `CORS_ORIGINS` value.
- Configure database backups and test a restore.
- Review Render plan limits and persistent storage.
- Verify social account URLs before launch.
- Monitor `/api/health` and test admin login after every deployment.
