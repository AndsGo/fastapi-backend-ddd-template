from typing import Any

from pydantic import BaseModel, Field


class AuditLogCreate(BaseModel):
    actor_id: str = Field(min_length=1, max_length=128)
    actor_name: str = Field(min_length=1, max_length=128)
    action: str = Field(min_length=1, max_length=128)
    resource_type: str = Field(min_length=1, max_length=128)
    resource_id: str = Field(min_length=1, max_length=128)
    before_snapshot: dict[str, Any] | None = None
    after_snapshot: dict[str, Any] | None = None
