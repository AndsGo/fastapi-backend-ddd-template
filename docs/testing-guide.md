# Testing Guide

Run the full suite:

```bash
python -m pytest
```

Run quality gates:

```bash
python -m ruff check .
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
python -m mypy app
```

Expected test groups:

- API smoke tests.
- Settings tests for the canonical `app.config` exports.
- Architecture tests for removed pre-migration packages and import boundaries.
- Logging tests.
- Redis key tests.
- Database engine/type/migration tests.
- Service tests.
- Job scheduler/worker/registry tests.
- Example module tests.

Behavior changes should add or update tests before handoff.

`app/config` is the canonical configuration package. Environment variables are read through `app/config/settings.py`, and settings are exposed through `app.config`; new tests and runtime code should import settings from `app.config`.
