# Architecture

This project is a backend-only FastAPI modular monolith template with strict
DDD-style dependency boundaries.

## Enterprise Layer Target

The project uses these canonical packages inside `app/`:

```text
app/domain          # Pure business rules, enums, value objects, policies
app/application     # Use cases, orchestration, DTOs, ports, application errors
app/infrastructure  # Database, cache, logging, jobs, external integrations
app/interface       # HTTP, job handlers, and composition roots
app/shared          # Stable cross-layer primitives
app/config          # Centralized configuration loading
```

Retired compatibility packages and the previous runtime `app/services` and
`app/core` layers are not part of the public template surface.

`app/config` is the canonical configuration package. Environment variables are
read through `app/config/settings.py`, and runtime code imports configuration
from `app.config`.

`app/domain` is canonical for pure business enums, value objects, and policies.

## Target Dependency Direction

```text
interface/http, interface/jobs/handlers -> application
interface composition roots -> infrastructure implementations -> application use cases
application -> domain
application -> application.ports
infrastructure.persistence.repositories -> application.ports
infrastructure.persistence.repositories -> infrastructure.persistence.models/domain
domain -> shared or standalone
config -> shared or standalone
```

`application.ports` contains provider-neutral protocols used by application use
cases. Infrastructure repositories implement those protocols and may import
`app.application.ports`, but application code must not import infrastructure.

Ports are application-owned capability requirements. A port describes what a
use case needs from the outside world, such as loading an aggregate, persisting
state, publishing a notification, or calling a gateway. Adapters are outer-layer
implementations of those requirements. For persistence, the SQLAlchemy
repositories under `app/infrastructure/persistence/repositories` are adapters
that satisfy repository ports.

This keeps the dependency direction inward: application code defines the
contract, and infrastructure conforms to it. Application use cases must not
import concrete SQLAlchemy repositories, sessions, models, Redis clients, HTTP
clients, or other infrastructure implementations. If a use case needs a new
external capability, add or extend a protocol under `app/application/ports` and
inject an implementation from an interface composition root.

Domain modules must not call repositories, job runners, HTTP adapters, or
application use cases. Cross-module workflows belong in application use cases.
Domain events may be used for follow-up workflows that do not require immediate
strong consistency.

Domain policy functions must be deterministic and framework-free. They may
return domain enum/value-object decisions, but must not import FastAPI,
SQLAlchemy, Pydantic, Redis, repositories, services, infrastructure, interface
adapters, config, or application modules.

## Context And Permissions

Execution context is explicit and framework-free. HTTP dependencies and job
adapters construct context objects and pass them into application use cases.

Authentication provider integrations belong in infrastructure after the
SSO/OAuth2/RBAC design is confirmed. Use-case permission checks belong in
application security policies. Pure business authorization rules belong in
domain code.

## Layers

```text
HTTP request
  -> app/interface/http endpoint
  -> app/application use case
  -> app/application/ports repository protocol
  -> app/infrastructure/persistence/repositories implementation
  -> app/infrastructure/persistence/models
  -> database
```

Rules:

- HTTP endpoints handle protocol concerns, request parsing, response models, and dependency injection.
- Job handlers adapt scheduled runs into application use case calls.
- Interface composition roots wire infrastructure repositories into application use cases.
- `app/application` owns use case orchestration, non-HTTP DTOs, ports, application errors, transaction boundaries, and cross-module coordination.
- `app/application` must not import interface adapters, infrastructure, or `app/services`.
- Repositories own SQLAlchemy queries and persistence details.
- Models define database tables only.
- Schemas define Pydantic request and response contracts.
- `app/config` owns settings and environment loading through `app/config/settings.py`.
- `app/interface/http/exception_handlers.py` owns FastAPI exception adaptation.
- `app/infrastructure/database` owns SQLAlchemy base, engine/session creation, and type helpers.
- `app/infrastructure/persistence/migrations` owns Alembic migrations.
- `app/infrastructure/persistence/models` owns database table mappings.
- `app/infrastructure/persistence/repositories` owns SQLAlchemy queries and persistence details.
- `app/infrastructure/cache` owns Redis client creation and key templates.
- `app/infrastructure/jobs` owns generic scheduler, worker, lock, registry, and runner infrastructure.
- `app/infrastructure/logging` owns runtime logging configuration.
- `app/interface/jobs/handlers` owns job handler delivery adapters.

## Example Module

The example slice demonstrates the expected module structure:

```text
app/interface/http/v1/endpoints/examples.py
app/interface/http/v1/router.py
app/interface/http/schemas/example.py
app/application/dto/example.py
app/application/ports/repositories.py
app/application/examples/create_example_item.py
app/application/examples/get_example_item.py
app/application/examples/list_example_items.py
app/application/examples/update_example_item.py
app/interface/jobs/handlers/example.py
app/infrastructure/persistence/models/example.py
app/infrastructure/persistence/repositories/example_repository.py
```

Use it as a pattern when adding real modules, then replace or remove it in
application projects.

## Extension Flow

1. Add domain enums, value objects, or policies under `app/domain` only if they are framework independent.
2. Add application repository or gateway protocols in `app/application/ports`.
3. Add application DTOs and use cases in `app/application`.
4. Add a model in `app/infrastructure/persistence/models`.
5. Add a repository implementation in `app/infrastructure/persistence/repositories`.
6. Add HTTP schemas in `app/interface/http/schemas`.
7. Add endpoints in `app/interface/http/v1/endpoints`.
8. Wire repositories into use cases in the HTTP or job composition root.
9. Register routes in `app/interface/http/v1/router.py`.
10. Add job handlers in `app/interface/jobs/handlers` when background execution is needed.
11. Add Alembic migration under `app/infrastructure/persistence/migrations` and tests.
12. Update docs.

## DDD Dependency Rules

```text
interface/http -> application
interface/jobs/handlers -> application
application -> domain/application.ports
infrastructure.persistence.repositories -> application.ports
infrastructure.persistence.repositories -> infrastructure.persistence.models/domain
domain -> no framework dependency
```

Ports and adapters rules:

- `app/application/ports` defines protocols; it must not import infrastructure.
- Application use cases depend on port protocols, not concrete adapters.
- Ports must stay technology-neutral: no FastAPI, SQLAlchemy, Redis, Pydantic, config, infrastructure, interface, or DTO imports.
- Infrastructure adapters may import application ports to declare the contract they implement.
- Interface composition roots instantiate infrastructure adapters and pass them into use cases.
- Endpoint modules and job handlers call use cases; they must not perform repository orchestration directly.

`app/interface/http` and `app/interface/jobs/handlers` are delivery adapters.
They must not orchestrate repositories directly outside explicit composition
roots.

`app/application` owns use cases, orchestration, application DTOs,
application-layer errors, and provider-neutral contracts. It depends on domain
code and application-layer DTOs/contracts; it must not import infrastructure or
interface adapters.

HTTP schemas are interface contracts. They must not import or subclass
application DTOs. Endpoint functions own the mapping from HTTP schema objects to
application command/query DTOs.

`app/services` is intentionally absent. Simple workflows live in application
use cases. Pure business rules live in domain policies, value objects, or domain
services under `app/domain`.
