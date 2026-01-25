# Project Information for AI Agents

## Technologies Used

### Backend
- **Python 3.14** - Programming language
- **FastAPI** - Web framework for building APIs
- **SQLAlchemy 2** - SQL toolkit and ORM
- **Alembic 1** - Database migration tool
- **Uvicorn** - ASGI server
- **uv** - Python package manager
- **pytest** - Testing framework
- **mypy** - Static type checker
- **ruff** - Linter and formatter

### Frontend
- **React 19** - UI library
- **TypeScript 5** - Programming language
- **Vite 7** - Build tool and dev server
- **React Router 7** - Routing library
- **openapi-fetch** - Type-safe API client
- **openapi-typescript** - OpenAPI type generator
- **Vitest 4** - Testing framework
- **ESLint 9** - Linter

## Folder Structure

```
/
├── backend/
│   ├── alembic/               # Database migration scripts
│   │   ├── versions/          # Migration version files
│   │   ├── env.py             # Alembic environment configuration
│   │   └── script.py.mako     # Migration template
│   ├── app/                   # Main application code
│   │   ├── api/               # API layer
│   │   │   ├── endpoints/     # API endpoint handlers
│   │   │   └── router.py      # API router configuration
│   │   ├── db.py              # Database configuration and session management
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── settings.py        # Application settings (env vars, config)
│   │   └── main.py            # Application entry point
│   ├── scripts/               # Utility scripts (e.g., OpenAPI export)
│   ├── alembic.ini            # Alembic configuration file
│   ├── pyproject.toml         # Python project configuration
│   ├── uv.lock                # Locked dependencies
│   └── app.db                 # SQLite database file (gitignored)
│
└── frontend/
    ├── src/
    │   ├── components/        # Reusable React components
    │   ├── pages/             # Page components
    │   ├── api_schema.d.ts    # Generated API types
    │   ├── App.tsx            # Root application component
    │   └── index.tsx          # Application entry point
    ├── package.json           # Node.js project configuration
    └── vite.config.ts         # Vite configuration (includes proxy to backend)
```

## Important Commands

### Setup
```bash
# Backend dependencies
cd backend
uv sync

# Frontend dependencies
cd frontend
npm install
```

### Testing & Quality
```bash
# Backend
cd backend
uv run ruff check      # Lint
uv run mypy            # Type check
uv run pytest          # Run tests (tests in app/**/test_*.py)

# Frontend
cd frontend
npm run lint           # Lint
npm run typecheck      # Type check
npm run test           # Run tests (tests in src/**/*.test.tsx)
```

### API Schema Generation
```bash
# Generate OpenAPI specification
cd backend
uv run python scripts/export_openapi.py

# Generate TypeScript types from OpenAPI
cd frontend
npm run generate-types
```

### Database Migrations

After modifying models in `app/models.py`, create a new migration:

```bash
cd backend

# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/

# Then apply it:
uv run alembic upgrade head
```

### Running the Application
```bash
# Start backend (in one terminal)
cd backend
uv run uvicorn app.main:app --reload

# Start frontend (in another terminal)
cd frontend
npm start
```

Ports:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173 (Vite default port)

The frontend proxies `/api` requests to http://localhost:8000 (configured in `vite.config.ts`).

## Contribution Guidelines

* You MUST run linter, type checker and tests if you modify the code.
* Your code MUST be warning free.
* You MUST create DB migrations and apply them to the database if you modify the models.
* If you modify code related to the API, you MUST update the OpenAPI specification and regenerate the API types.

## Coding Guidelines

### Python

* Use type hints for all function signatures and class attributes.
* Follow ruff's strict linting rules (configured in `pyproject.toml`).

### TypeScript

* PREFER using the `@/` alias for all imports over relative imports.
* Use CSS nested selectors to simplify CSS complexity.
* Isolate CSS into separate files for each component using CSS modules (e.g., `ComponentName.module.css`).