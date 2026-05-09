from app.application.jobs.contracts import JobContext, JobResult, JobRouter
from app.infrastructure.cache.keys import RedisKey, build_cache_key
from app.infrastructure.cache.redis import close_redis_client, get_redis_client
from app.infrastructure.database.base import Base, TimestampMixin
from app.infrastructure.database.engine import build_engine_options, validate_database_url
from app.infrastructure.database.session import get_db, get_engine, get_session_local
from app.infrastructure.database.types import case_sensitive_string
from app.infrastructure.jobs.registry import JobRegistry
from app.infrastructure.jobs.run_worker import ConcurrentScheduledRunWorker
from app.infrastructure.jobs.scheduler import DistributedScheduler
from app.infrastructure.logging.config import JsonFormatter, configure_logging, get_logger
from app.infrastructure.persistence.models.example import ExampleItem
from app.infrastructure.persistence.models.scheduled_job import ScheduledJob
from app.infrastructure.persistence.repositories.example_repository import ExampleItemRepository
from app.infrastructure.persistence.repositories.scheduled_job_repository import (
    ScheduledJobRepository,
    ScheduledJobRunRepository,
)


def test_target_database_namespace_exports_core_database_helpers() -> None:
    assert Base.metadata is not None
    assert TimestampMixin is not None
    assert callable(build_engine_options)
    assert callable(validate_database_url)
    assert callable(get_engine)
    assert callable(get_session_local)
    assert callable(get_db)
    assert case_sensitive_string(64) is not None


def test_target_persistence_namespace_exports_models_and_repositories() -> None:
    assert ExampleItem.__tablename__ == "example_items"
    assert ScheduledJob.__tablename__ == "scheduled_jobs"
    assert ExampleItemRepository.model is ExampleItem
    assert ScheduledJobRepository.model is ScheduledJob
    assert ScheduledJobRunRepository.model.__tablename__ == "scheduled_job_runs"


def test_target_cache_namespace_exports_cache_helpers() -> None:
    assert build_cache_key(RedisKey.EXAMPLE_ITEM, item_id=1, prefix="tpl") == (
        "tpl:example:item:1"
    )
    assert callable(get_redis_client)
    assert callable(close_redis_client)


def test_target_logging_namespace_exports_logging_helpers() -> None:
    assert JsonFormatter is not None
    assert callable(configure_logging)
    assert callable(get_logger)


def test_job_contracts_and_infrastructure_are_split() -> None:
    assert JobContext is not None
    assert JobResult().status == "succeeded"
    assert JobRouter is not None
    assert JobRegistry is not None
    assert ConcurrentScheduledRunWorker is not None
    assert DistributedScheduler is not None
