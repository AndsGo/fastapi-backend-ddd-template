from app.application.jobs.contracts import JobContext, JobHandler, JobResult, JobRouter


class UnknownJobTypeError(Exception):
    def __init__(self, job_type: str) -> None:
        self.job_type = job_type
        super().__init__(f"Unknown job type: {job_type}")


class JobRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, JobHandler] = {}

    def register(self, job_type: str, handler: JobHandler) -> None:
        if job_type in self._handlers:
            raise ValueError(f"Job type already registered: {job_type}")

        self._handlers[job_type] = handler

    def include_router(self, router: JobRouter) -> None:
        for job_type, handler in router.handlers.items():
            self.register(job_type, handler)

    def get(self, job_type: str) -> JobHandler:
        try:
            return self._handlers[job_type]
        except KeyError as exc:
            raise UnknownJobTypeError(job_type) from exc

    def execute(self, context: JobContext) -> JobResult:
        handler = self.get(context.job_type)
        return handler(context)
