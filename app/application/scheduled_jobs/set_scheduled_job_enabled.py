from typing import Any

from app.application.errors import NotFoundError
from app.application.ports import ScheduledJobRepositoryPort
from app.domain.enums import ScheduledJobStatus


class SetScheduledJobEnabledUseCase:
    def __init__(self, repository: ScheduledJobRepositoryPort) -> None:
        self.repository = repository

    def execute(self, job_id: int, *, enabled: bool) -> Any:
        job = self.repository.get(job_id)
        if job is None:
            raise NotFoundError("scheduled_job", job_id)
        status = ScheduledJobStatus.enabled if enabled else ScheduledJobStatus.disabled
        return self.repository.update(job, {"status": status})
