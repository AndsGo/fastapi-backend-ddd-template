from app.domain.enums import (
    ScheduledJobRunStatus,
    ScheduledJobStatus,
    TaskStatus,
)
from app.domain.scheduled_jobs.policies import (
    initial_scheduled_job_run_status,
    initial_scheduled_job_status,
)


def test_task_status_values_are_stable() -> None:
    assert [status.value for status in TaskStatus] == [
        "pending",
        "running",
        "succeeded",
        "failed",
        "canceled",
    ]


def test_scheduled_job_status_values_are_stable() -> None:
    assert [status.value for status in ScheduledJobStatus] == [
        "enabled",
        "disabled",
        "archived",
    ]


def test_scheduled_job_run_status_values_are_stable() -> None:
    assert [status.value for status in ScheduledJobRunStatus] == [
        "pending",
        "running",
        "succeeded",
        "failed",
        "canceled",
    ]


def test_scheduled_job_initial_status_policy_returns_enabled() -> None:
    assert initial_scheduled_job_status() == ScheduledJobStatus.enabled


def test_scheduled_job_run_initial_status_policy_returns_pending() -> None:
    assert initial_scheduled_job_run_status() == ScheduledJobRunStatus.pending
