from app.application.dto.scheduled_job import ScheduledJobCreate, ScheduledJobRunCreate
from app.application.scheduled_jobs.create_scheduled_job import CreateScheduledJobUseCase
from app.application.scheduled_jobs.create_scheduled_job_run import CreateScheduledJobRunUseCase
from app.application.scheduled_jobs.set_scheduled_job_enabled import SetScheduledJobEnabledUseCase
from app.domain.enums import ScheduledJobRunStatus, ScheduledJobStatus


class InMemoryScheduledJobRepository:
    def __init__(self) -> None:
        self.entities = {
            1: {
                "id": 1,
                "code": "example-noop",
                "status": ScheduledJobStatus.disabled,
            }
        }
        self.created_payload = None
        self.updated_payload = None

    def create(self, payload: dict):
        self.created_payload = payload
        return {"id": 2, **payload}

    def get(self, resource_id: int):
        return self.entities.get(resource_id)

    def update(self, entity: dict, payload: dict):
        self.updated_payload = payload
        entity.update(payload)
        return dict(entity)


class InMemoryScheduledJobRunRepository:
    def __init__(self) -> None:
        self.created_payload = None

    def list_by_job(self, job_id: int, skip: int = 0, limit: int = 100):
        return []

    def create(self, payload: dict):
        self.created_payload = payload
        return {"id": 1, **payload}


def test_create_scheduled_job_use_case_creates_job_with_enabled_status() -> None:
    job_repository = InMemoryScheduledJobRepository()
    payload = ScheduledJobCreate(
        code="retry-failed-examples",
        name="Retry failed examples",
        cron_expression="0 2 * * *",
        timezone="Asia/Shanghai",
        job_type="example.retry_failed",
        payload={"max_retry": 3},
    )

    result = CreateScheduledJobUseCase(job_repository).execute(payload)

    assert job_repository.created_payload["status"] == ScheduledJobStatus.enabled
    assert result["code"] == "retry-failed-examples"


def test_create_scheduled_job_use_case_preserves_distributed_job_fields() -> None:
    job_repository = InMemoryScheduledJobRepository()
    payload = ScheduledJobCreate(
        code="distributed-example-sync",
        name="Distributed example sync",
        cron_expression="*/5 * * * *",
        job_type="example.distributed_sync",
        lock_ttl_seconds=60,
        max_runtime_seconds=900,
        misfire_policy="run_once",
        concurrent_policy="forbid",
    )

    result = CreateScheduledJobUseCase(job_repository).execute(payload)

    assert job_repository.created_payload["lock_ttl_seconds"] == 60
    assert job_repository.created_payload["max_runtime_seconds"] == 900
    assert job_repository.created_payload["misfire_policy"] == "run_once"
    assert job_repository.created_payload["concurrent_policy"] == "forbid"
    assert result["lock_ttl_seconds"] == 60
    assert result["max_runtime_seconds"] == 900
    assert result["misfire_policy"] == "run_once"
    assert result["concurrent_policy"] == "forbid"


def test_set_scheduled_job_enabled_use_case_enables_and_disables_job() -> None:
    job_repository = InMemoryScheduledJobRepository()
    use_case = SetScheduledJobEnabledUseCase(job_repository)

    enabled = use_case.execute(1, enabled=True)
    disabled = use_case.execute(1, enabled=False)

    assert enabled["status"] == ScheduledJobStatus.enabled
    assert disabled["status"] == ScheduledJobStatus.disabled


def test_create_scheduled_job_run_use_case_creates_run_with_pending_status() -> None:
    job_repository = InMemoryScheduledJobRepository()
    run_repository = InMemoryScheduledJobRunRepository()
    payload = ScheduledJobRunCreate(triggered_by="system")

    result = CreateScheduledJobRunUseCase(job_repository, run_repository).execute(1, payload)

    assert run_repository.created_payload["status"] == ScheduledJobRunStatus.pending
    assert run_repository.created_payload["job_id"] == 1
    assert result["triggered_by"] == "system"

