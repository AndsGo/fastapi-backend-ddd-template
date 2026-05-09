from typing import Any

from app.application.dto.scheduled_job import ScheduledJobCreate
from app.application.ports import ScheduledJobRepositoryPort
from app.domain.scheduled_jobs.policies import initial_scheduled_job_status


class CreateScheduledJobUseCase:
    def __init__(self, repository: ScheduledJobRepositoryPort) -> None:
        self.repository = repository

    def execute(self, payload: ScheduledJobCreate) -> Any:
        data = payload.model_dump()
        data["status"] = initial_scheduled_job_status()
        data["last_run_at"] = None
        return self.repository.create(data)
