from typing import Any, Protocol


class BaseRepositoryPort(Protocol):
    def list(self, skip: int = 0, limit: int = 100) -> list[Any]: ...

    def get(self, resource_id: int) -> Any | None: ...

    def create(self, payload: dict[str, Any]) -> Any: ...

    def update(self, entity: Any, payload: dict[str, Any]) -> Any: ...


class ExampleItemRepositoryPort(BaseRepositoryPort, Protocol):
    def get_by_code(self, code: str) -> Any | None: ...


class AuditLogRepositoryPort(BaseRepositoryPort, Protocol):
    pass


class ScheduledJobRepositoryPort(BaseRepositoryPort, Protocol):
    pass


class ScheduledJobRunRepositoryPort(BaseRepositoryPort, Protocol):
    def list_by_job(self, job_id: int, skip: int = 0, limit: int = 100) -> list[Any]: ...
