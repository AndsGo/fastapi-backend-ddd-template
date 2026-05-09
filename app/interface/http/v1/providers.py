from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.audit_logs.list_audit_logs import ListAuditLogsUseCase
from app.application.examples.create_example_item import CreateExampleItemUseCase
from app.application.examples.get_example_item import GetExampleItemUseCase
from app.application.examples.list_example_items import ListExampleItemsUseCase
from app.application.examples.update_example_item import UpdateExampleItemUseCase
from app.application.scheduled_jobs.create_scheduled_job import CreateScheduledJobUseCase
from app.application.scheduled_jobs.create_scheduled_job_run import (
    CreateScheduledJobRunUseCase,
)
from app.application.scheduled_jobs.get_scheduled_job import GetScheduledJobUseCase
from app.application.scheduled_jobs.list_scheduled_job_runs import (
    ListScheduledJobRunsUseCase,
)
from app.application.scheduled_jobs.list_scheduled_jobs import ListScheduledJobsUseCase
from app.application.scheduled_jobs.set_scheduled_job_enabled import (
    SetScheduledJobEnabledUseCase,
)
from app.application.scheduled_jobs.update_scheduled_job import UpdateScheduledJobUseCase
from app.infrastructure.database.session import get_db
from app.infrastructure.persistence.repositories.audit_log_repository import (
    AuditLogRepository,
)
from app.infrastructure.persistence.repositories.example_repository import (
    ExampleItemRepository,
)
from app.infrastructure.persistence.repositories.scheduled_job_repository import (
    ScheduledJobRepository,
    ScheduledJobRunRepository,
)


def get_example_item_repository(db: Session = Depends(get_db)) -> ExampleItemRepository:
    return ExampleItemRepository(db)


def get_list_example_items_use_case(
    repository: ExampleItemRepository = Depends(get_example_item_repository),
) -> ListExampleItemsUseCase:
    return ListExampleItemsUseCase(repository)


def get_create_example_item_use_case(
    repository: ExampleItemRepository = Depends(get_example_item_repository),
) -> CreateExampleItemUseCase:
    return CreateExampleItemUseCase(repository)


def get_get_example_item_use_case(
    repository: ExampleItemRepository = Depends(get_example_item_repository),
) -> GetExampleItemUseCase:
    return GetExampleItemUseCase(repository)


def get_update_example_item_use_case(
    repository: ExampleItemRepository = Depends(get_example_item_repository),
) -> UpdateExampleItemUseCase:
    return UpdateExampleItemUseCase(repository)


def get_audit_log_repository(db: Session = Depends(get_db)) -> AuditLogRepository:
    return AuditLogRepository(db)


def get_list_audit_logs_use_case(
    repository: AuditLogRepository = Depends(get_audit_log_repository),
) -> ListAuditLogsUseCase:
    return ListAuditLogsUseCase(repository)


def get_scheduled_job_repository(db: Session = Depends(get_db)) -> ScheduledJobRepository:
    return ScheduledJobRepository(db)


def get_scheduled_job_run_repository(db: Session = Depends(get_db)) -> ScheduledJobRunRepository:
    return ScheduledJobRunRepository(db)


def get_list_scheduled_jobs_use_case(
    repository: ScheduledJobRepository = Depends(get_scheduled_job_repository),
) -> ListScheduledJobsUseCase:
    return ListScheduledJobsUseCase(repository)


def get_create_scheduled_job_use_case(
    repository: ScheduledJobRepository = Depends(get_scheduled_job_repository),
) -> CreateScheduledJobUseCase:
    return CreateScheduledJobUseCase(repository)


def get_get_scheduled_job_use_case(
    repository: ScheduledJobRepository = Depends(get_scheduled_job_repository),
) -> GetScheduledJobUseCase:
    return GetScheduledJobUseCase(repository)


def get_update_scheduled_job_use_case(
    repository: ScheduledJobRepository = Depends(get_scheduled_job_repository),
) -> UpdateScheduledJobUseCase:
    return UpdateScheduledJobUseCase(repository)


def get_set_scheduled_job_enabled_use_case(
    repository: ScheduledJobRepository = Depends(get_scheduled_job_repository),
) -> SetScheduledJobEnabledUseCase:
    return SetScheduledJobEnabledUseCase(repository)


def get_list_scheduled_job_runs_use_case(
    job_repository: ScheduledJobRepository = Depends(get_scheduled_job_repository),
    run_repository: ScheduledJobRunRepository = Depends(get_scheduled_job_run_repository),
) -> ListScheduledJobRunsUseCase:
    return ListScheduledJobRunsUseCase(job_repository, run_repository)


def get_create_scheduled_job_run_use_case(
    job_repository: ScheduledJobRepository = Depends(get_scheduled_job_repository),
    run_repository: ScheduledJobRunRepository = Depends(get_scheduled_job_run_repository),
) -> CreateScheduledJobRunUseCase:
    return CreateScheduledJobRunUseCase(job_repository, run_repository)
