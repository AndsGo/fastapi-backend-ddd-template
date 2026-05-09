from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import ScheduledJobStatus


class ScheduledJobCreate(BaseModel):
    code: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    cron_expression: str = Field(min_length=1, max_length=128)
    timezone: str = Field(default="UTC", min_length=1, max_length=64)
    job_type: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    next_run_at: datetime | None = None
    lock_ttl_seconds: int = Field(default=60, ge=1)
    max_runtime_seconds: int = Field(default=900, ge=1)
    misfire_policy: str = Field(default="run_once", min_length=1, max_length=32)
    concurrent_policy: str = Field(default="forbid", min_length=1, max_length=32)


class ScheduledJobUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    cron_expression: str | None = Field(default=None, min_length=1, max_length=128)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    job_type: str | None = Field(default=None, min_length=1, max_length=128)
    status: ScheduledJobStatus | None = None
    payload: dict[str, Any] | None = None
    next_run_at: datetime | None = None
    lock_ttl_seconds: int | None = Field(default=None, ge=1)
    max_runtime_seconds: int | None = Field(default=None, ge=1)
    misfire_policy: str | None = Field(default=None, min_length=1, max_length=32)
    concurrent_policy: str | None = Field(default=None, min_length=1, max_length=32)


class ScheduledJobRunCreate(BaseModel):
    triggered_by: str = Field(default="system", min_length=1, max_length=128)
