# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bank-grade UPDG (Unified Project Digital Group) platform covering full project lifecycle management, outsourcing resource pool, automated cost accounting, and AI-assisted document generation.

- **Backend:** `python-backend/` — Python FastAPI monolith
- **Frontend:** `frontend/` — Vue 3.4 + Vite + Element Plus + Pinia + TypeScript
- **Vite proxy:** `/api/*` → `localhost:8001` (Python backend)

## Key Commands

### Python Backend (`python-backend/`)

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload` | Run dev server with hot reload |
| `python init_db.py` | Drop/create all tables + seed admin user |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic revision --autogenerate -m "description"` | Generate migration from model changes |
| `pytest` | Run all tests |
| `ruff check app/ && ruff format app/` | Lint + format |

### Frontend (`frontend/`)

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run dev` | Start Vite dev server (port 3000) |
| `npm run build` | TypeScript check + production build |
| `npm run lint` | ESLint with auto-fix |
| `npm run type-check` | `vue-tsc --noEmit` |

### Docker Compose (`python-backend/`)

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start PostgreSQL, Redis, MinIO |
| `docker compose down` | Stop all services |

## Architecture

### Python Backend Tech Stack

- **Framework:** FastAPI 0.110+ with Uvicorn (async)
- **ORM:** SQLAlchemy 2.0 async + asyncpg (SQLite for dev via `aiosqlite`)
- **Migrations:** Alembic 1.13
- **Auth:** python-jose (JWT, HS256) + gmssl (SM3)
- **Cache/Queue:** Redis 7 + Celery 5.3
- **Storage:** MinIO
- **Database:** PostgreSQL 16 (prod), SQLite (dev)

### Python Backend Structure

```
python-backend/
├── app/
│   ├── main.py                 # FastAPI app factory, registers 14 routers
│   ├── config.py               # Pydantic settings from .env
│   ├── database.py             # Async engine + session factory (auto-detects SQLite)
│   ├── dependencies.py         # Auth deps: get_current_user, get_current_admin_user
│   ├── core/
│   │   ├── schemas.py          # ApiResponse (code="SUCCESS"), PageResult (records field)
│   │   └── security.py         # SM3 hash, JWT create/verify/decode
│   ├── api/                    # 14 FastAPI routers (auth, system, project, business, cost, resource, timesheet, knowledge, workflow, notify, quality, file, audit, ai)
│   ├── models/                 # 57 SQLAlchemy ORM models by domain
│   └── workers/                # Celery task definitions
├── alembic/                    # Database migrations
└── tests/                      # pytest suite
```

## API Patterns

### Python FastAPI Patterns

- **Response envelope** — `ApiResponse(code="SUCCESS", message="...", data={...})`
- **`code` is a string**, not numeric — frontend checks `code === 'SUCCESS'`
- **Pagination** uses `PageResult(total=..., page=..., size=..., records=[...])` with `records` field (not `items`)
- **Legacy alias routes** — many endpoints have `/list`, `/create` aliases for frontend compatibility
- **Never use `**kwargs` in FastAPI route handlers** — causes 422 "Field required" errors
- **Auth** — SM3 password hash + JWT, `get_current_user` / `get_current_admin_user` dependencies

### Frontend API Proxy

Vite dev server proxies `/api/*` to `http://localhost:8001` (Python backend).

## Important Notes

- **Frontend proxies to port 8001** — run Python uvicorn on `--port 8001`, not 8000
- **Python `code="SUCCESS"` not `code="200"`** — common bug; all Python responses must use string codes
- **Test coverage target:** >= 80% (per README convention).
