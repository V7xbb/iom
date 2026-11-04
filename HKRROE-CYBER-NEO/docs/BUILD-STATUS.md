# Build and test report

Checked in the packaging environment on 2026-11-04:

- Python bytecode compilation: passed for the FastAPI application and Alembic scripts.
- Backend automated tests: `python -m pytest -q` passed (3 tests).
- SQLite fresh database migration: `alembic upgrade head` passed.
- Legacy starter SQLite schema migration: passed; missing project and verification columns were added.
- Backend integration smoke: admin bootstrap/login, protected admin APIs, project and news creation, verification record creation/approval, public lookup, visit recording, and password/token invalidation passed.
- Frontend TS/TSX syntax transpilation: passed.
- Full Next.js type-check/production build: not completed here because npm dependency installation timed out and node packages were not installed in this environment. Render will run `npm install && npm run build` from the frontend root.
- Live Render deployment and PostgreSQL cloud connectivity: not performed in this environment.

The frontend has CSS perspective and float motion on the mascot artwork and social cubes. It does not yet include a rigged, interactive WebGL character model. The mascot is an illustrated image asset, not a true skeletal 3D model.
