# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bank-grade UPDG platform covering full project lifecycle management, outsourcing resource pool, automated cost accounting, and AI-assisted document generation. 16 microservices + 1 shared library + Vue3 frontend + Python FastAPI backend.

Two parallel backend implementations share one Vue 3 frontend:

| Backend | Path | Status |
|---------|------|--------|
| **Java Microservices** | `microservices/` | Production (17 services) |
| **Python FastAPI** | `python-backend/` | Active development (monolith) |

- **Frontend:** `frontend/` — Vue 3.4 + Vite + Element Plus + Pinia + TypeScript
- **Vite proxy:** `/api/*` → `localhost:8001` (Python backend)

## Key Commands

### Maven (bundled at `apache-maven-3.9.6/bin/mvn` — no `mvnw`)

| Command | Description |
|---------|-------------|
| `mvn clean package -DskipTests` | Build all modules |
| `mvn spring-boot:run -pl microservices/<service> -Dspring-boot.run.profiles=dev` | Run a single service in dev mode |
| `mvn test` | Run all tests |
| `mvn test -pl microservices/<service>` | Run tests for a specific service |
| `mvn jacoco:report` | Generate coverage report |

### Scripts

| Script | Description |
|--------|-------------|
| `bash scripts/start-services.sh` | Start all microservices on assigned ports |
| `bash scripts/run-tests.sh` | Integration test suite (11 phases, ~55 tests) |

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

### Java Microservices Tech Stack

- **Framework:** Spring Boot 3.2.5, Spring Cloud 2023.0.1, Spring Cloud Alibaba 2023.0.1.0
- **ORM:** MyBatis-Plus 3.5.9 (with mybatis-spring 3.0.3 — critical compatibility fix for Spring Boot 3.2.x)
- **Database:** MySQL 8.0 (prod) / H2 in-memory MODE=MySQL (dev) / 达梦 DM8 (prod 信创)
- **Message Queue:** RocketMQ (async events, workflow triggers, delayed messages)
- **Workflow Engine:** Flowable 7.0.1 (BPMN)
- **Security:** Bouncy Castle (SM2/SM3/SM4), JWT (JJWT), SSO adapter

### Python Backend Tech Stack

- **Framework:** FastAPI 0.110+ with Uvicorn (async)
- **ORM:** SQLAlchemy 2.0 async + asyncpg (SQLite for dev via `aiosqlite`)
- **Migrations:** Alembic 1.13
- **Auth:** python-jose (JWT, HS256) + gmssl (SM3)
- **Cache/Queue:** Redis 7 + Celery 5.3
- **Storage:** MinIO
- **Database:** PostgreSQL 16 (prod), SQLite (dev)

### Dev Mode Configuration (Java)

Each service's `application-dev.yml` uses an isolated H2 database:

- **Nacos discovery/config disabled** in dev mode
- **Redis auto-configuration excluded** in dev mode
- **Flyway migrations** from `classpath:db/h2` (when enabled)
- **MyBatis-Plus SQL logging** enabled (stdout)
- **Flowable disabled** in updg-workflow dev profile (DDL incompatible with H2)

### Microservices (Java)

| Service | Port | Description | Key Dependencies |
|---------|------|-------------|------------------|
| **common** | N/A | Shared library (NOT a service) | MyBatis-Plus, JWT, Bouncy Castle, Hutool, Redis, Flowable (provided), RocketMQ (provided) |
| **updg-system** | 8082 | System management (users, depts, roles, dicts) | Web, Flyway, H2 |
| **updg-auth** | 8083 | Authentication (login, token refresh, SSO) | Web, Redis, H2 |
| **updg-project** | 8084 | Project lifecycle (init, progress, changes, EVM) | Web, RocketMQ, H2, Flyway |
| **updg-cost** | 8085 | Cost accounting and EVM | Web, H2, Flyway |
| **updg-timesheet** | 8086 | Timesheet entry and approval | Web, H2, Flyway |
| **updg-resource** | 8087 | Outsourcing resource pool | Web, H2, Flyway |
| **updg-knowledge** | 8088 | Knowledge management (RAG) | Web, H2, Flyway |
| **updg-workflow** | 8089 | Workflow engine (Flowable BPMN) | Web, Flowable, RocketMQ, MySQL (not H2) |
| **updg-ai** | 8090 | AI document generation, NLQ queries | Web, WebFlux, MinIO, EasyExcel |
| **updg-gateway** | 8080 | Spring Cloud Gateway | Gateway, Nacos, Sentinel |
| **updg-report** | 8091 | Report service | Web, H2, Flyway |
| **updg-notify** | 8092 | Notification service (WeChat/Email/SMS) | Web, RocketMQ, H2, Flyway |
| **updg-integration** | 8093 | External system adapters (HR, Finance, DevOps) | Web, H2, Flyway |
| **updg-file** | 8094 | File service (MinIO) | Web, MinIO, H2, Flyway |
| **updg-audit** | 8095 | Audit logging | Web, H2, Flyway |
| **updg-quality** | 8096 | Quality management | Web, H2, Flyway |

**Note:** `microservices/notify/` has no `pom.xml` and is NOT a registered Maven module. The actual notification service is `updg-notify`.

### Common Module (`microservices/common/`)

Package prefix: `com.bank.updg.common`

- **`model.ApiResponse`** — Unified API response envelope `{code, message, data, timestamp}` with `success()` / `error()` factories
- **`exception.BusinessException`** — Runtime exception wrapping `ErrorCodeEnum`
- **`exception.GlobalExceptionHandler`** — `@RestControllerAdvice` handling validation, business, and generic errors
- **`model.enums.ErrorCodeEnum`** — All error codes with domain prefixes (AUTH_*, SYS_*, PROJECT_*, etc.)
- **`security.JwtUtil`** — JWT token generation/parsing/validation
- **`security.RequiresPermission`** + `security.Logical` — Method-level permission annotation
- **`util.DesensitizationUtil`** — Data masking (phone, ID card, name, amount)
- **`util.CryptoUtil`** — SM2/SM3/SM4 encryption
- **`util.LogUtil`** — Structured logging with traceId/MDC
- **`mq.RocketMQProducer`** — Producer with send/sendDelay/sendTransaction
- **`flow.FlowableService`** — Workflow deployment/start/approval utilities

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

### Java Controller Conventions

- `@RestController`, `@RequestMapping("/api/<domain>/...")`
- Constructor injection via `@RequiredArgsConstructor` (Lombok)
- All endpoints return `ApiResponse<T>`
- Pagination uses `page` (1-based) and `limit` query params
- Dynamic queries via MyBatis-Plus `LambdaQueryWrapper`
- `@RequiresPermission` annotation for method-level auth

### Python FastAPI Patterns

- **Response envelope** — `ApiResponse(code="SUCCESS", message="...", data={...})`
- **`code` is a string**, not numeric — frontend checks `code === 'SUCCESS'`
- **Pagination** uses `PageResult(total=..., page=..., size=..., records=[...])` with `records` field (not `items`)
- **Legacy alias routes** — many endpoints have `/list`, `/create` aliases for frontend compatibility
- **Never use `**kwargs` in FastAPI route handlers** — causes 422 "Field required" errors
- **Auth** — SM3 password hash + JWT, `get_current_user` / `get_current_admin_user` dependencies

### Error Handling (Java)

```java
throw new BusinessException(ErrorCodeEnum.PROJECT_NOT_FOUND);
throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "pv, ev, ac are required");
```

Global handler maps exceptions to safe client messages with appropriate HTTP status codes.

### Frontend API Proxy

Vite dev server proxies `/api/*` to `http://localhost:8001` (Python backend). When testing Java services, either:
- Call the service directly by its port (e.g., `localhost:8083/api/auth/login`)
- Or update the proxy target in `frontend/vite.config.ts`

## Maven Profiles (Java)

- **`dev`** (default) — H2 database, Nacos disabled, console logging
- **`prod`** — MySQL, Nacos enabled, structured JSON logging
- **`dm8`** — 达梦 DM8 driver for 信创 compliance

## Important Notes

- **No `mvnw`** exists in the repo. Use `apache-maven-3.9.6/bin/mvn` or a system-installed Maven.
- **`microservices/notify/`** is not a Maven module (no pom.xml). Use `updg-notify` instead.
- **updg-workflow** requires a real MySQL database in dev mode — Flowable DDL is incompatible with H2.
- **MyBatis-Plus 3.5.9 + mybatis-spring 3.0.3** is a deliberate version pin. Do not downgrade mybatis-spring to 2.x (causes `factoryBeanObjectType` error with Spring Boot 3.2.x).
- **Frontend proxies to port 8001** — run Python uvicorn on `--port 8001`, not 8000
- **Python `code="SUCCESS"` not `code="200"`** — common bug; all Python responses must use string codes
- **Test coverage target:** >= 80% (per README convention).
