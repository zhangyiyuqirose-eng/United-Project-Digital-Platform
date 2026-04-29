# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PMO Digital Operations Management Platform — Python/FastAPI backend replacing 17 Java Spring Boot microservices. Monolithic FastAPI architecture serving all 14 domain APIs on a single process, sharing one Vue 3 frontend with the Java codebase at `../microservices/`.

- **14 domain modules** (auth, system, project, business, cost, resource, timesheet, knowledge, notify, workflow, audit, quality, file, ai)
- **57 database tables** via SQLAlchemy 2.0 async ORM
- **SM3 password hashing** (国密) + JWT authentication, compatible with existing Java users
- **Vue 3 frontend** at `../frontend/` — zero modifications, proxies `/api/*` to `localhost:8001`

## Key Commands

### Backend

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload` | Run dev server with hot reload |
| `python init_db.py` | Drop/create all tables + seed admin user |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic revision --autogenerate -m "description"` | Generate migration from model changes |
| `pytest` | Run all tests |
| `pytest -k test_name` | Run a specific test |
| `pytest --cov=app --cov-report=term-missing` | Run tests with coverage |
| `ruff check app/` | Lint code |
| `ruff format app/` | Format code |

### Frontend (in `../frontend/`)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server (port 3000, proxies to `:8001`) |
| `npm run build` | Production build |
| `npm run type-check` | TypeScript check |

### Docker Compose

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start PostgreSQL, Redis, MinIO |
| `docker compose down` | Stop all services |

## Architecture

### Tech Stack

- **Framework:** FastAPI 0.110+ with Uvicorn (async)
- **ORM:** SQLAlchemy 2.0 async + asyncpg (SQLite for dev via `aiosqlite`)
- **Migrations:** Alembic 1.13
- **Auth:** python-jose (JWT, HS256) + gmssl (SM3)
- **Cache/Queue:** Redis 7 + Celery 5.3
- **Storage:** MinIO
- **Database:** PostgreSQL 16 (prod), SQLite (dev)

### Project Structure

```
python-backend/
├── app/
│   ├── main.py                 # FastAPI app factory, registers 14 routers
│   ├── config.py               # Pydantic settings from .env
│   ├── database.py             # Async engine + session factory (auto-detects SQLite)
│   ├── dependencies.py         # Auth deps: get_current_user, get_current_admin_user
│   ├── exceptions.py           # ResourceNotFoundError, ValidationError, BusinessError
│   ├── middleware.py           # CORS, auth, error handling
│   ├── core/
│   │   ├── schemas.py          # ApiResponse (code="SUCCESS"), PageResult (records field)
│   │   └── security.py         # SM3 hash, JWT create/verify/decode
│   ├── api/                    # 14 FastAPI routers (17 Java controllers → 14 modules)
│   │   ├── auth.py             # /api/auth/login, /refresh, /logout, /register
│   │   ├── system.py           # /api/system/users, roles, depts, permissions, announcements
│   │   ├── project.py          # /api/project/list, tasks, risks, WBS, gantt, EVM
│   │   ├── business.py         # /api/business/contracts, payments, suppliers, customers
│   │   ├── cost.py             # /api/cost/budgets, alerts, EVM, expenses
│   │   ├── resource.py         # /api/resource/pools, outsourcing, performance, leave
│   │   ├── timesheet.py        # /api/timesheet/list, approvals, reports
│   │   ├── knowledge.py        # /api/knowledge/docs, templates, reviews, compliance
│   │   ├── workflow.py         # /api/workflow/start, my-tasks, status
│   │   ├── notify.py           # /api/notify/messages, templates
│   │   ├── quality.py          # /api/quality/defects, metrics
│   │   ├── file.py             # /api/file/upload, download, list
│   │   ├── audit.py            # /api/audit/logs
│   │   └── ai.py               # /api/ai/* (AI features)
│   ├── models/                 # 57 SQLAlchemy ORM models by domain
│   ├── schemas/                # Pydantic request schemas (inline in api/ files)
│   ├── services/               # Service layer (currently empty, logic in routers)
│   ├── workers/                # Celery task definitions
│   └── integrations/           # External system adapters
├── alembic/                    # Database migrations
│   └── versions/0001_initial_schema.py
├── tests/                      # pytest suite
│   ├── conftest.py             # SQLite in-memory fixtures, test client
│   └── test_*.py
├── init_db.py                  # Seed script (admin/Admin123!)
├── pyproject.toml
├── .env                        # Dev config (SQLite)
└── docker-compose.yml          # PostgreSQL + Redis + MinIO stack
```

### API Patterns

**Response envelope** — all endpoints return `ApiResponse`:
```python
ApiResponse(code="SUCCESS", message="success", data={...})
```

- `code` is a **string** matching Java `ErrorCodeEnum` values: `"SUCCESS"`, `"NOT_FOUND"`, `"PARAM_ERROR"`, `"UNAUTHORIZED"`, `"INTERNAL_ERROR"`
- **NOT** numeric codes like `"200"` — the frontend checks `code === 'SUCCESS'`
- Pagination uses `PageResult(total=..., page=..., size=..., records=[...])` with `records` field (not `items`)

**Router registration** in `main.py`:
```python
app.include_router(auth_router, prefix="/api/auth")
app.include_router(system_router, prefix="/api/system")
# ... each domain under /api/{domain}
```

**Legacy alias routes** — many endpoints have `/list`, `/create` aliases for frontend compatibility:
```python
@router.get("/list")  # frontend calls /api/project/list
async def list_alias(...): return await list(...)
```

**Never use `**kwargs` in alias routes** — FastAPI cannot introspect `**kwargs`, causing 422 errors. Always declare explicit parameters.

### Authentication

- SM3 password hash → compare with `verify_password(plain, hashed)`
- JWT with `create_token(user_id, extra_claims)` → `Authorization: Bearer <token>`
- `get_current_user` dependency extracts user from JWT
- `get_current_admin_user` requires admin role

### Database

- Dev: SQLite (`sqlite+aiosqlite:///./updg_dev.db`) — no connection pool config
- Prod: PostgreSQL (`postgresql+asyncpg://...`) — pool_size=20, max_overflow=10
- `database.py` auto-detects SQLite and disables pooling
- Models use `UUIDPrimaryKeyMixin` (VARCHAR(64) pk) and `TimestampMixin` (create_time/update_time)
- Run `python init_db.py` to recreate schema and seed test data

## Important Notes

- **Frontend proxies to port 8001** — run uvicorn on `--port 8001`, not 8000
- **No `schemas/` or `services/` yet** — Pydantic schemas are inline in api files, business logic lives in router functions
- **Workflow module is placeholder** — `/api/workflow/*` endpoints return stub data; full BPM requires Camunda/Flowable integration
- **MinIO is optional** — file upload/download works but bucket auto-creation on each upload is inefficient
- **`code="SUCCESS"` not `code="200"`** — this was a common bug; all responses must use string codes
- **Never use `**kwargs` in FastAPI route handlers** — causes 422 "Field required" errors
