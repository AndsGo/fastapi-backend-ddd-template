from app.domain.enums import ScheduledJobRunStatus, ScheduledJobStatus


def initial_scheduled_job_status() -> ScheduledJobStatus:
    return ScheduledJobStatus.enabled


def initial_scheduled_job_run_status() -> ScheduledJobRunStatus:
    return ScheduledJobRunStatus.pending
