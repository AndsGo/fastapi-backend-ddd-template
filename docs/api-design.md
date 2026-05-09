# API Design

All API routes are registered under `/api/v1`.

## Endpoint Rules

- Endpoints stay thin.
- Use Pydantic schemas for request and response contracts.
- Compose FastAPI providers and use-case injection in `app/interface/http/v1/providers.py`.
- Keep `app/interface/http/v1/dependencies.py` for request, user, and security-style HTTP dependencies.
- Endpoints call application use cases.
- Put cross-module orchestration in `app/application`.
- Put database access in `app/infrastructure/persistence/repositories`.
- Return paginated lists for collection endpoints.

## Error Shape

Application exceptions are returned as:

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Resource not found",
  "details": {}
}
```

Use `app/application/errors.py` for reusable application errors. FastAPI-specific
exception adaptation belongs in `app/interface/http/exception_handlers.py`.
