# Database migrations

Run `alembic upgrade head` from the `backend` directory after configuring `DATABASE_URL`.
The initial revision creates all SQLAlchemy models. For future schema changes, add a new Alembic revision; do not edit an already deployed revision.
