from app.application.security.permissions import PermissionChecker
from app.shared.context import Actor, CorrelationId, RequestContext, TenantId


def test_request_context_is_framework_free_value_object() -> None:
    context = RequestContext(
        actor=Actor(id="user-1", roles=("admin",), permissions=frozenset({"orders:create"})),
        tenant_id=TenantId(value="tenant-1"),
        correlation_id=CorrelationId(value="corr-1"),
    )

    assert context.actor.id == "user-1"
    assert context.actor.roles == ("admin",)
    assert context.actor.permissions == frozenset({"orders:create"})
    assert context.tenant_id.value == "tenant-1"
    assert context.correlation_id.value == "corr-1"


def test_permission_checker_reads_context_permissions() -> None:
    context = RequestContext(
        actor=Actor(id="user-1", roles=("operator",), permissions=frozenset({"jobs:run"})),
        tenant_id=TenantId(value="tenant-1"),
        correlation_id=CorrelationId(value="corr-1"),
    )

    checker = PermissionChecker()

    assert checker.has_permission(context, "jobs:run") is True
    assert checker.has_permission(context, "jobs:delete") is False


def test_enterprise_layer_packages_are_importable() -> None:
    import app.config
    import app.domain
    import app.infrastructure
    import app.infrastructure.cache
    import app.infrastructure.database
    import app.infrastructure.jobs
    import app.infrastructure.logging
    import app.infrastructure.persistence
    import app.infrastructure.persistence.models
    import app.infrastructure.persistence.repositories
    import app.interface
    import app.interface.http
    import app.interface.http.schemas
    import app.interface.http.v1
    import app.interface.jobs
    import app.interface.jobs.handlers
    import app.shared
    from app.config import Settings, settings

    assert app.domain is not None
    assert app.infrastructure is not None
    assert app.interface is not None
    assert app.config is not None
    assert Settings is not None
    assert settings is not None
