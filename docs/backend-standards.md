# Backend Standards

## Layering

- Interface: HTTP protocol, dependency injection, and job delivery adapters.
- Application: use cases, ports, application DTOs, errors, and cross-module orchestration.
- Infrastructure repository: SQLAlchemy queries.
- Infrastructure model: table definitions only.
- Domain: pure business enums, value objects, and deterministic policies.
- Config: centralized settings and environment loading.

## Code Rules

- Keep endpoints thin.
- Do not query the database from endpoints.
- Do not reintroduce runtime `app/services`.
- Do not import infrastructure from application use cases.
- Do not read environment variables outside `app/config/settings.py`.
- `app/config` is the canonical configuration package; `app/config/settings.py` reads environment variables.
- `app/domain` is canonical for pure business enums, value objects, and policies.
- Domain policy functions must be deterministic and framework-free. They may return domain enum/value-object decisions, but must not import FastAPI, SQLAlchemy, Pydantic, Redis, repositories, services, infrastructure, interface adapters, config, or application modules.
- Add tests for behavior changes.
- Update related docs before handoff.

## Commands

```bash
python -m ruff check .
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
python -m mypy app
python -m pytest
```
