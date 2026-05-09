# Job Guide

The job system is generic infrastructure for work that should not run directly inside HTTP requests.

## Runtime Pieces

- `scheduled_jobs`: recurring job definitions.
- `scheduled_job_runs`: trigger and execution records.
- `DistributedScheduler`: scans due jobs and creates pending runs.
- `ConcurrentScheduledRunWorker`: claims pending runs and executes handlers with thread-pool concurrency.
- `app/infrastructure/jobs`: scheduler, worker, locks, logging, registry, and infrastructure runner helpers.
- `app/interface/jobs/handlers`: delivery adapters for scheduled runs.
- `JobRouter`: decorator-style handler registration.
- `JobRegistry`: runtime handler lookup and execution.
- Redis: distributed locks and heartbeats.

## Register A Job

Create an application use case:

```python
from app.application.jobs.contracts import JobContext, JobResult

class RunNoopJobUseCase:
    def execute(self, context: JobContext) -> JobResult:
        return JobResult(processed_count=1, succeeded_count=1)
```

Expose it through a job handler adapter in `app/interface/jobs/handlers`:

```python
from app.application.jobs.contracts import JobContext, JobResult, JobRouter
from app.application.examples.run_noop_job import RunNoopJobUseCase

router = JobRouter()

@router.handler("example.noop")
def noop(context: JobContext) -> JobResult:
    return RunNoopJobUseCase().execute(context)
```

Register infrastructure routers in the composition root at `app/interface/jobs/runner.py`.

Handlers must accept `JobContext` and return `JobResult`.

## Run Manually

```bash
python -m app.interface.jobs.runner scheduler --once
python -m app.interface.jobs.runner worker --once --max-workers 4
```

## Design Rules

- The scheduler only creates due runs; it does not execute business behavior.
- The worker only claims runs and dispatches handlers.
- Each worker task gets its own SQLAlchemy session.
- Job handlers are delivery adapters and should call application use cases.
- Application use cases own domain behavior orchestration and may call domain code and application ports.
- Job composition adapters wire infrastructure repositories directly into use cases through `app/application/ports` protocols.
- Use Redis for locks and coordination, not as the source of truth.
- Database rows remain the source of truth for definitions and run history.
