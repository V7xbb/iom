# Render deployment — HKRROE CYBER NEO v3

1. Upload the complete project directory to a Git repository.
2. In Render, choose **New → Blueprint** and connect the repository containing `render.yaml`.
3. Set the requested `ADMIN_USERNAME` and `ADMIN_PASSWORD` values. Use a unique password of 12+ characters.
4. Keep generated `JWT_SECRET_KEY` and `VISITOR_HASH_SECRET` values private.
5. Apply the Blueprint. Render builds the FastAPI service (including the Alembic migration), PostgreSQL database, and Next.js service.
6. Once both web services are live, open the frontend URL, go to `/dashboard`, and sign in.
7. Check `/api/health`. It should return `status: ok` and `database: connected`.

If the API reports a CORS error, verify the `CORS_ORIGINS` environment variable on the API is exactly the deployed frontend origin, including `https://` and without a trailing slash. Then redeploy the API.

For Render free plan limitations, sleeping services, and database retention, consult the current Render dashboard and plan documentation before relying on it for production.
