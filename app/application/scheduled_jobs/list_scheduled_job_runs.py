from typing import Any

from app.application.errors import NotFoundError
from app.application.ports import ScheduledJobRepositoryPort, ScheduledJobRunRepositoryPort


class ListScheduledJobRunsUseCase:
    def __init__(
        self,
        job_repository: ScheduledJobRepositoryPort,
        run_repository: ScheduledJobRunRepositoryPort,
    ) -> None:
        self.job_repository = job_repository
        self.run_repository = run_repository

    def execute(self, *, job_id: int, skip: int = 0, limit: int = 100) -> list[Any]:
        if self.job_repository.get(job_id) is None:
            raise NotFoundError("scheduled_job", job_id)
        return self.run_repository.list_by_job(job_id, skip=skip, limit=limit)
