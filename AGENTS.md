# AGENTS.md

## Project Context

Backend-only FastAPI framework template for reusable DDD-oriented modular monoliths.

Core dependency direction:

```text
interface/http, interface/jobs/handlers -> application -> domain/application.ports
infrastructure.persistence.repositories -> application.ports
infrastructure.persistence.repositories -> infrastructure.persistence.models
domain -> no framework dependency
```

## Hard Rules For Agents

- Do not add frontend code unless explicitly requested.
- Do not add `docker-compose.yml` unless explicitly requested.
- `app/interface/http` endpoints and `app/interface/jobs/handlers` are delivery adapters; they call application use cases, not services/repositories directly.
- Cross-module orchestration belongs in `app/application`; do not reintroduce a runtime `app/services` layer.
- `app/application` must not import interface adapters or infrastructure directly.
- HTTP/job composition adapters wire infrastructure repositories directly into use cases through `app/application/ports` protocols.
- Repositories own SQLAlchemy queries; models are persistence-only.
- Domains are pure business code and must not depend on FastAPI, SQLAlchemy, Redis, or Pydantic.
- `app/domain` is canonical for pure business enums, value objects, and policies.
- Domain policy functions must be deterministic and framework-free. They may return domain enum/value-object decisions, but must not import FastAPI, SQLAlchemy, Pydantic, Redis, repositories, services, infrastructure, interface adapters, config, or application modules.
- HTTP schemas stay in `app/interface/http/schemas`.
- Non-HTTP use case DTOs stay in `app/application/dto`.
- HTTP schemas must not import or subclass application DTOs; endpoints convert schemas into use-case DTOs.
- `app/application/ports` must stay technology-neutral and must not import FastAPI, SQLAlchemy, Redis, Pydantic, config, interface, infrastructure, or application DTOs.
- Only explicit composition roots may import infrastructure from `app/interface`.
- Keep auth and permissions as placeholders until the stakeholder confirms the target SSO/OAuth2/RBAC design.
- Use environment variables for configuration. Do not hard-code credentials.
- Do not read environment variables outside `app/config/settings.py`.
- `app/config` is the canonical configuration package; `app/config/settings.py` reads environment variables.
- Add or update tests for behavior changes.
- After completing a requirement, update the related documentation before final handoff.
- Run verification commands before claiming completion.

## Dependency Rules

```text
interface/http -> infrastructure except explicit composition roots
interface/jobs.handlers -> infrastructure except explicit composition roots
application -> interface/infrastructure/services
infrastructure.persistence.repositories -> interface/application.dto/application.jobs/application.security/services/infrastructure.jobs
infrastructure.persistence.models -> interface/application/services/repositories/infrastructure.jobs
domain -> fastapi/sqlalchemy/pydantic/redis/repositories/services/infrastructure/interface/config/application/utils
```

These are forbidden imports. `.importlinter` enforces part of this boundary. If a change needs to violate them, stop and discuss the architecture first.

## Infrastructure Rules

- `DATABASE_URL` selects PostgreSQL or MySQL; MySQL URLs must include `charset=utf8mb4`.
- Engine isolation is `READ COMMITTED`; unique string business keys use `app.infrastructure.database.types.case_sensitive_string()`.
- Persisted datetimes must be UTC.
- Alembic migrations must use portable SQLAlchemy types unless dialect-specific behavior is explicitly guarded and documented.
- Redis keys must be defined in `app/infrastructure/cache/keys.py` and built with `build_cache_key()`.
- Update relevant docs when architecture, setup, jobs, DB schema, config, or testing changes.
- Primary docs: `docs/architecture.md`, `docs/project-framework-standards.md`, `docs/database-design.md`, `docs/development-guide.md`, `docs/job-guide.md`, `docs/redis-support.md`.

## Important Commands

```bash
python -m pytest
python -m ruff check .
python -m mypy app
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
uvicorn app.main:app --reload
alembic revision --autogenerate -m "message"
alembic upgrade head
```

