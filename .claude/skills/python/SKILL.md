---
name: python-backend-guidelines
description: Python + FastAPI + SQLAlchemy + Alembic coding guidelines for building maintainable, testable, and secure backends. Use this skill when generating or modifying Python backend code.
---

# Agent Guidelines (Python Backend)

You are an expert in modern Python backend development. You write maintainable, secure, and well-tested code aligned with current Python ecosystem best practices and this repository’s conventions.

## Language & Formatting Conventions

- Use **type hints everywhere** (functions, return types, attributes). Keep `pyright` strict.
- Prefer `from __future__ import annotations` in modules that declare lots of types (especially SQLAlchemy models and shared utilities).
- Prefer **explicit, readable code** over cleverness.
- Use **f-strings** for interpolation.
- Keep imports clean and layered:
  - stdlib
  - third-party
  - local (`from app...`)
- Follow `ruff` formatting (line-length 120, double quotes).
- Use `TYPE_CHECKING` for imports needed only for typing to avoid runtime cycles.

## Python Best Practices

- Prefer **pure functions** and small units with clear inputs/outputs.
- Validate inputs early; use **guard clauses** and keep the happy path obvious.
- Avoid global mutable state (especially shared sessions/clients).
- Prefer `pathlib.Path` for filesystem paths.
- Use timezone-aware timestamps where applicable; treat UTC as the default for storage/transport.
- Don’t catch broad exceptions unless you re-raise or translate them into a well-defined error response.

## FastAPI (API Design)

- Keep endpoints thin:
  - Parse/validate with Pydantic models
  - Delegate to a small service/function when logic grows
- Use correct HTTP semantics:
  - `201 Created` with `Location` header for newly created resources
  - `204 No Content` for successful deletes
  - `404 Not Found` for missing resources
  - `422` is handled by FastAPI/Pydantic for validation errors
- Prefer `http.HTTPStatus` for status codes (clearer intent than magic numbers).

## Testing (pytest)

- Prefer deterministic, isolated tests.
- Use behavior-focused test names and assertions.
- When testing endpoints:
  - Use `fastapi.testclient.TestClient` for sync routes
  - Assert status codes and response shape (not exact timestamps/messages unless required)
- Avoid test coupling through shared state:
  - Prefer a temporary DB / per-test transaction pattern when the suite grows.
- In case of integration tests involving the database, **always use unique data** for codes, descriptions, etc. to avoid conflicts with existing data.

## Security & Reliability

- Treat all external input as untrusted.
- Don’t leak secrets or internal traces in responses.
- Prefer explicit, user-safe error messages; keep internal details in logs (if/when logging is added).
- Use least privilege for configuration and avoid committing secrets (use `.env` locally).
