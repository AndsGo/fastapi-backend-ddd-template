from app.application.examples.run_noop_job import RunNoopJobUseCase
from app.application.jobs.contracts import JobContext, JobResult, JobRouter

router = JobRouter()


@router.handler("example.noop")
def noop(context: JobContext) -> JobResult:
    return RunNoopJobUseCase().execute(context)
