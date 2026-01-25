# Coding with AI - Sample Project

## Prerequisites

- Python 3.14
- Node.JS >= LTS
- [uv](https://docs.astral.sh/uv/)

## Installing Dependencies

```bash
cd backend
uv sync
```

```bash
cd frontend
npm install
```

## Testing the Code

```bash
cd backend
uv run ruff check # Linting the code
uv run mypy # Type checking the code
uv run pytest # Running the tests
```

```bash
cd frontend
npm run lint # Linting the code
npm run typecheck # Type checking the code
npm run test # Running the tests
```

## Open API Specification

Generate the Open API specification file:

```bash
cd backend
uv run python scripts/export_openapi.py
```

Generate the API schema types:

```bash
cd frontend
npm run generate-types
```

## Database Setup and Management

This project uses **SQLAlchemy 2** as the ORM and **Alembic** for database migrations.

## Database Configuration

The database URL is configured in `app/settings.py` and defaults to SQLite. You can override this by setting the `DATABASE_URL` environment variable or creating a `.env` file.

How to manage the database:

```bash
# Run all pending migrations
uv run alembic upgrade head
```

After modifying models in `app/models.py`, create a new migration:

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/

# Then apply it:
uv run alembic upgrade head
```

## Running the Project

To run the project, you must start the backend and the frontend in the background:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

```bash
cd frontend
npm start
```

Note that the frontend (vite) contains a proxy to the backend API (see [`vite.config.ts`](./frontend/vite.config.ts)).
