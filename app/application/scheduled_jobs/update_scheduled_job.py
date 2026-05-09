from typing import Any

from app.application.dto.scheduled_job import ScheduledJobUpdate
from app.application.errors import NotFoundError
from app.application.ports import ScheduledJobRepositoryPort


class UpdateScheduledJobUseCase:
    def __init__(self, repository: ScheduledJobRepositoryPort) -> None:
        self.repository = repository

    def execute(self, job_id: int, payload: ScheduledJobUpdate) -> Any:
        job = self.repository.get(job_id)
        if job is None:
            raise NotFoundError("scheduled_job", job_id)
        return self.repository.update(job, payload.model_dump(exclude_unset=True))
