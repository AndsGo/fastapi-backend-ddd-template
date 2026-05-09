# Project Framework Standards

This document defines the reusable backend framework standards for projects
based on this template.

## Scope

Use this template for backend-only FastAPI services that need a strict
DDD-oriented modular monolith structure, relational database migrations,
optional Redis, scheduled jobs, structured logging, tests, linting, and type
checking.

## Standard Structure

```text
app/
  interface/
    http/
      exception_handlers.py
      v1/
        endpoints/
        dependencies.py
        providers.py
        router.py
      schemas/
    jobs/
      handlers/
  config/
    settings.py
  infrastructure/
    cache/
      keys.py
      redis.py
    database/
      base.py
      engine.py
      session.py
      types.py
    jobs/
      cron.py
      locks.py
      logging.py
      registry.py
      run_worker.py
      scheduler.py
    logging/
      config.py
    persistence/
      migrations/
      models/
      repositories/
  domain/
    enums.py
    scheduled_jobs/
      policies.py
  application/
    dto/
    errors.py
    ports/
    examples/
  shared/
tests/
docs/
```

New delivery adapter work uses `app/interface`, infrastructure work uses
`app/infrastructure`, application orchestration uses `app/application`, and pure
business work uses `app/domain`.

## Enterprise Placement Guide

```text
Write an API endpoint               -> app/interface/http
Write request/response schemas      -> app/interface/http/schemas
Write a business use case           -> app/application/<module>
Write repository/gateway protocols  -> app/application/ports
Write application exceptions        -> app/application/errors.py
Write HTTP exception handlers       -> app/interface/http/exception_handlers.py
Write core business rules           -> app/domain/<module>
Write domain enums/value objects    -> app/domain/<module>
Write deterministic domain policies -> app/domain/<module>/policies.py
Write a database table              -> app/infrastructure/persistence/models
Write SQLAlchemy queries            -> app/infrastructure/persistence/repositories
Integrate Redis or external tools   -> app/infrastructure
Read environment variables          -> app/config/settings.py
Add cross-layer primitives          -> app/shared, only when stable and non-business-specific
```

`app/config` is the canonical configuration package. Environment variables are
read through `app/config/settings.py`, and runtime code imports configuration
from `app.config`.

`app/domain` is canonical for pure business enums, value objects, and policies.

`application.ports` contains provider-neutral interfaces and contracts used by
application use cases. Infrastructure adapters may import these ports to make
their contract explicit, but application code must not import infrastructure.

Ports are owned by the application layer. They describe required capabilities,
not implementation choices. For example, a use case may depend on an
`ExampleItemRepositoryPort` that can `get_by_code()` and `create()`, while the
SQLAlchemy repository in infrastructure is only one adapter that satisfies that
protocol.

Adapters live outside the application layer. HTTP providers, job runners, and
future composition roots instantiate concrete infrastructure adapters and inject
them into use cases. Do not inject SQLAlchemy sessions, models, Redis clients,
or concrete infrastructure repositories directly into application code without
going through an application port.

## Layering Rules

Allowed direction:

```text
interface/http -> application
interface/jobs/handlers -> application
application -> domain
application -> application.ports
infrastructure.persistence.repositories -> application.ports
infrastructure.persistence.repositories -> infrastructure.persistence.models/domain
```

Forbidden direction:

```text
application -> interface
application -> infrastructure
application -> services
domain -> application/interface/infrastructure/config
models -> interface/application/repositories/jobs
repositories -> interface/application.dto/application.jobs/application.security/services/jobs
endpoints -> database queries
interface/http endpoints -> infrastructure directly
interface/jobs/handlers -> infrastructure directly
```

Explicit composition roots, such as `app/interface/http/v1/providers.py` and
`app/interface/jobs/runner.py`, may wire infrastructure implementations into
application use cases.

Ports and adapters rules:

- Define external capability requirements as protocols in `app/application/ports`.
- Keep port method signatures focused on use-case needs, not ORM convenience.
- Keep ports technology neutral: no FastAPI, SQLAlchemy, Redis, Pydantic, config, interface, infrastructure, or application DTO imports.
- Let infrastructure repositories or gateways implement those protocols.
- Keep adapter construction in interface composition roots.
- Do not import concrete infrastructure adapters from `app/application`.

## Automated Architecture Gate

The dependency rules are enforced by Import Linter in `.importlinter`.

CI rejects direct imports that violate these boundaries:

- Interface modules must not bypass application use cases. Narrow composition-root exceptions exist for `app/interface/http/v1/providers.py` and `app/interface/jobs/runner.py`.
- Application use cases must not import interface adapters, infrastructure, or `app/services`.
- Application use cases must depend on `app/application/ports` protocols for external capabilities.
- Application ports must stay technology-neutral and must not import application DTOs.
- Persistence repositories must not import interface, DTOs, use cases, services, or job infrastructure.
- Persistence models must not import upper layers.
- Domain code must stay framework-free.
- HTTP schemas must not import application DTOs; endpoints convert HTTP schemas into application DTOs.
- Only explicit composition roots may import infrastructure from `app/interface`.
- Internal runtime code must import configuration from `app.config`.
- Environment variables may be read only in `app/config/settings.py`.

Run the architecture gate locally:

```bash
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
```

## Adding A Module

1. Add framework-free domain enums, value objects, or policies in `app/domain` when the module needs them.
2. Add repository or gateway protocols in `app/application/ports`.
3. Add DTOs and use cases in `app/application`.
4. Add model in `app/infrastructure/persistence/models`.
5. Add repository implementation in `app/infrastructure/persistence/repositories`.
6. Add HTTP schemas in `app/interface/http/schemas`.
7. Add endpoint in `app/interface/http/v1/endpoints`.
8. Wire infrastructure repositories into use cases in `app/interface/http/v1/providers.py` or the relevant job composition root.
9. Register endpoint in `app/interface/http/v1/router.py`.
10. Add job handlers in `app/interface/jobs/handlers` if needed.
11. Create an Alembic migration in `app/infrastructure/persistence/migrations`.
12. Add tests.
13. Update docs.

Use `ExampleItem` as the reference implementation.

## Jobs

- Job definitions live in `scheduled_jobs`.
- Run history lives in `scheduled_job_runs`.
- Handlers are registered with `JobRouter`.
- Handler signature is `JobContext -> JobResult`.
- Scheduler and worker live in `app/infrastructure/jobs`.
- Job handlers are delivery adapters and should call application use cases.
- Cross-module orchestration belongs in `app/application`, not in handlers or endpoints.

## Application Layer

`app/application` is the DDD application layer.

Responsibilities:

- Use case orchestration.
- Non-HTTP input/output DTOs.
- Provider-neutral ports.
- Application-layer errors.
- Cross-module coordination.
- Transaction boundary ownership.
- Idempotency and permission checks when they are use-case concerns.

Rules:

- API schemas should be converted into application DTOs.
- HTTP schemas are interface contracts and must not subclass or import application DTOs.
- Jobs should call application use cases.
- Application use cases may call ports and domain code, but must not import infrastructure directly.
- HTTP and job composition adapters wire infrastructure repositories into use cases.
- Application code must not return FastAPI responses.
- Runtime `app/services` is intentionally absent; do not reintroduce it.

## Domain Layer

`app/domain` is the canonical package for pure business enums, value objects,
domain services, and policies.

Domain policy functions must be deterministic and framework-free. They may
return domain enum/value-object decisions, but must not import FastAPI,
SQLAlchemy, Pydantic, Redis, repositories, services, infrastructure, interface
adapters, config, or application modules.

## Database

- `DATABASE_URL` selects PostgreSQL or MySQL.
- MySQL URLs must include `charset=utf8mb4`.
- Engine isolation is `READ COMMITTED`.
- Unique string business keys use `case_sensitive_string()`.
- Persisted datetimes are UTC.
- Migrations must be portable unless explicitly dialect guarded.

## Redis

- Redis key templates live in `app/infrastructure/cache/keys.py`.
- Use `build_cache_key()`.
- Do not scatter hard-coded Redis keys in use cases or endpoints.

## Logging

- Runtime logs are JSON Lines by default.
- Runtime logging configuration lives in `app/infrastructure/logging`.
- Prefer stdout in prod.
- Local rotating file output is optional through `LOG_OUTPUT=file` or `LOG_OUTPUT=both`.
- Do not log secrets.

## Delivery Checklist

Before handoff:

```bash
python -m ruff check .
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
python -m mypy app
python -m pytest
```

Also check:

- `.env.example` is updated for new configuration.
- Migrations match model changes.
- Documentation reflects behavior changes.
- No real secrets are committed.
