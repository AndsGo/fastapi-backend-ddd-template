from typing import Any

from app.application.dto.scheduled_job import ScheduledJobRunCreate
from app.application.errors import NotFoundError
from app.application.ports import ScheduledJobRepositoryPort, ScheduledJobRunRepositoryPort
from app.domain.scheduled_jobs.policies import initial_scheduled_job_run_status


class CreateScheduledJobRunUseCase:
    def __init__(
        self,
        job_repository: ScheduledJobRepositoryPort,
        run_repository: ScheduledJobRunRepositoryPort,
    ) -> None:
        self.job_repository = job_repository
        self.run_repository = run_repository

    def execute(self, job_id: int, payload: ScheduledJobRunCreate) -> Any:
        if self.job_repository.get(job_id) is None:
            raise NotFoundError("scheduled_job", job_id)
        data = payload.model_dump()
        data["job_id"] = job_id
        data["status"] = initial_scheduled_job_run_status()
        return self.run_repository.create(data)
