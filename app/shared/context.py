from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TenantId:
    value: str


@dataclass(frozen=True, slots=True)
class CorrelationId:
    value: str


@dataclass(frozen=True, slots=True)
class Actor:
    id: str | None
    roles: tuple[str, ...] = ()
    permissions: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class RequestContext:
    actor: Actor
    tenant_id: TenantId | None
    correlation_id: CorrelationId
