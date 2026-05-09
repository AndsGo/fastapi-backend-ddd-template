from typing import Any

from app.application.errors import NotFoundError
from app.application.ports import ScheduledJobRepositoryPort


class GetScheduledJobUseCase:
    def __init__(self, repository: ScheduledJobRepositoryPort) -> None:
        self.repository = repository

    def execute(self, job_id: int) -> Any:
        job = self.repository.get(job_id)
        if job is None:
            raise NotFoundError("scheduled_job", job_id)
        return job
