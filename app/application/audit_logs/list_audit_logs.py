from typing import Any

from app.application.ports import AuditLogRepositoryPort


class ListAuditLogsUseCase:
    def __init__(self, repository: AuditLogRepositoryPort) -> None:
        self.repository = repository

    def execute(self, *, skip: int = 0, limit: int = 100) -> list[Any]:
        return self.repository.list(skip=skip, limit=limit)
