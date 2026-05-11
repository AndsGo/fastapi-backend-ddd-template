# FastAPI Backend Template

Reusable backend-only FastAPI template for modular monolith services.

[中文文档](README.zh-CN.md)

## Requirements

- Python 3.11 or newer.
- PostgreSQL or MySQL when running the persistence layer.
- Redis when running distributed scheduled jobs or Redis-backed cache features.

## What Is Included

- FastAPI API versioning and dependency injection.
- SQLAlchemy models, repositories, sessions, and Alembic migrations.
- PostgreSQL and MySQL support through `DATABASE_URL`.
- Redis client and centralized Redis key templates.
- Scheduled job definitions, scheduler, concurrent worker, and job registry.
- Runtime JSON logging to stdout and optional rotating local files.
- Strict DDD-oriented interface, application, domain, ports, and infrastructure layering.
- A small `examples` module that demonstrates the expected structure.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Set `DATABASE_URL` in `.env` for your database. Redis is optional unless you run
distributed jobs.

`app/config` is the canonical configuration package. Environment variables are read through `app/config/settings.py`, and settings are exposed through `app.config`.

`app/domain` is canonical for pure business enums, value objects, and policies.

Key environment variables:

- `APP_ENV`: runtime environment name, such as `local`, `staging`, or `production`.
- `DATABASE_URL`: SQLAlchemy database URL for PostgreSQL or MySQL.
- `SECRET_KEY`: application secret used by security helpers; replace the example value.
- `BACKEND_CORS_ORIGINS`: JSON array of allowed browser origins.
- `REDIS_URL`: Redis connection URL for cache and distributed job coordination.
- `REDIS_PREFIX`: prefix applied to Redis keys owned by this application.

## Database Migrations

```bash
alembic upgrade head
```

Create new migrations after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

## Run API

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Run Jobs

```bash
python -m app.interface.jobs.runner scheduler --interval-seconds 10
python -m app.interface.jobs.runner worker --interval-seconds 5 --worker-id worker-1 --max-workers 4
```

Installed console script:

```bash
backend-jobs worker --once --max-workers 4
```

## Verify

```bash
python -m pytest
python -m ruff check .
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
python -m mypy app
```

## Use As A Template

Use the existing `examples` module as the reference implementation when adding a new
business area:

- Add framework-free domain enums, value objects, and policies under `app/domain`.
- Add repository or gateway protocols under `app/application/ports`.
- Add non-HTTP use-case DTOs and use cases under `app/application`.
- Add database models under `app/infrastructure/persistence/models`.
- Put database access in `app/infrastructure/persistence/repositories`.
- Add HTTP request and response schemas under `app/interface/http/schemas`.
- Add configuration settings in `app/config/settings.py` and import them from `app.config`.
- Put use-case orchestration in `app/application`; put pure business rules in `app/domain`.
- Expose HTTP routes from `app/interface/http/v1/endpoints` and register them in `app/interface/http/v1/router.py`.
- Wire infrastructure repositories into use cases in `app/interface/http/v1/providers.py` or the relevant job composition root.
- Add tests in `tests` for repositories, application use cases, and endpoints.
- Update the related documentation under `docs`.

`app/application/ports` belongs to the application layer. A port describes an
external capability a use case needs; infrastructure repositories and gateways
are adapters that satisfy those protocols. Application use cases depend on
ports, never on concrete SQLAlchemy repositories or other infrastructure
implementations.

HTTP schemas and application DTOs are separate contracts. Endpoints convert
request schemas into application command/query DTOs before calling use cases.

Domain policy functions must be deterministic and framework-free. They may return
domain enum/value-object decisions, but must not import FastAPI, SQLAlchemy,
Pydantic, Redis, repositories, services, infrastructure, config, application, or
interface adapters.

The project intentionally keeps authentication and authorization as placeholders. Confirm
the target SSO, OAuth2, or RBAC design before using this template for production access
control.

## Continuous Integration

GitHub Actions runs the same verification commands on pushes and pull requests to `main`.
GitLab CI runs the same gate through `.gitlab-ci.yml`.

## Main Docs

- [Architecture](docs/architecture.md)
- [DDD quickstart](docs/ddd-quickstart.md)
- [Development guide](docs/development-guide.md)
- [Database design](docs/database-design.md)
- [Job guide](docs/job-guide.md)
- [Project framework standards](docs/project-framework-standards.md)
