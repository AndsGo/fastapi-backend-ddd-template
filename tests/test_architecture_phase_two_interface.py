from fastapi.routing import APIRoute

from app.application.jobs.contracts import JobContext
from app.interface.http.schemas.audit_log import AuditLogResponse
from app.interface.http.schemas.example import ExampleItemCreate, ExampleItemResponse
from app.interface.http.schemas.scheduled_job import ScheduledJobCreate, ScheduledJobResponse
from app.interface.http.v1.router import api_router
from app.interface.jobs.handlers.example import noop
from app.interface.jobs.handlers.example import router as interface_example_job_router
from app.main import app


def route_operations(routes: list[APIRoute]) -> set[tuple[str, str]]:
    operations: set[tuple[str, str]] = set()
    for route in routes:
        for method in route.methods or set():
            operations.add((route.path, method))
    return operations


def test_app_uses_target_interface_router() -> None:
    route_paths = {route.path for route in app.routes}

    assert "/api/v1/health" in route_paths
    assert "/api/v1/examples" in route_paths

    operations = route_operations([route for route in app.routes if isinstance(route, APIRoute)])

    assert ("/api/v1/health", "GET") in operations
    assert ("/api/v1/examples", "GET") in operations
    assert ("/api/v1/examples", "POST") in operations
    assert ("/api/v1/examples/{item_id}", "GET") in operations
    assert ("/api/v1/examples/{item_id}", "PATCH") in operations
    assert ("/api/v1/scheduled-jobs/{job_id}/runs", "GET") in operations
    assert ("/api/v1/scheduled-jobs/{job_id}/runs", "POST") in operations


def test_target_http_router_registers_existing_endpoints() -> None:
    route_paths = {route.path for route in api_router.routes}

    assert "/health" in route_paths
    assert "/examples" in route_paths
    assert "/audit-logs" in route_paths
    assert "/scheduled-jobs" in route_paths


def test_target_http_schema_namespace_exports_current_schemas() -> None:
    assert ExampleItemCreate(code="code", name="Name").code == "code"
    assert ExampleItemCreate.__module__ == "app.interface.http.schemas.example"
    assert ExampleItemResponse.model_fields["code"] is not None
    assert AuditLogResponse.model_fields["action"] is not None
    scheduled_job = ScheduledJobCreate(
        code="example-noop",
        name="Example Noop",
        cron_expression="*/5 * * * *",
        job_type="example.noop",
    )

    assert scheduled_job.job_type == "example.noop"
    assert ScheduledJobResponse.model_fields["job_type"] is not None


def test_target_job_handler_adapter_registers_noop_handler() -> None:
    assert "example.noop" in interface_example_job_router.handlers


def test_target_noop_job_handler_returns_success_result() -> None:
    context = JobContext(
        job_id=1,
        run_id=10,
        job_type="example.noop",
        payload={},
        triggered_by="manual",
        worker_id="worker-1",
        db=object(),
        redis=object(),
    )

    result = noop(context)

    assert result.status == "succeeded"
    assert result.processed_count == 1
    assert result.succeeded_count == 1
    assert result.failed_count == 0
