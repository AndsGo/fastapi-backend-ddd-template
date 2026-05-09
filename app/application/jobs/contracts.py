from collections.abc import Callable
from dataclasses import dataclass, field
from inspect import Signature, signature
from typing import Any, TypeVar, get_type_hints


@dataclass(frozen=True)
class JobContext:
    job_id: int
    run_id: int
    job_type: str
    payload: dict[str, Any]
    triggered_by: str
    worker_id: str
    db: Any
    redis: Any


@dataclass(frozen=True)
class JobResult:
    status: str = "succeeded"
    processed_count: int = 0
    succeeded_count: int = 0
    failed_count: int = 0
    details: dict[str, Any] = field(default_factory=dict)


JobHandler = Callable[[JobContext], JobResult]
DecoratedJobHandler = TypeVar("DecoratedJobHandler", bound=Callable[..., JobResult])


class JobRouter:
    def __init__(self) -> None:
        self.handlers: dict[str, JobHandler] = {}

    def handler(self, job_type: str) -> Callable[[DecoratedJobHandler], DecoratedJobHandler]:
        def decorator(handler: DecoratedJobHandler) -> DecoratedJobHandler:
            if job_type in self.handlers:
                raise ValueError(f"Job type already registered: {job_type}")
            _validate_job_handler_signature(handler)
            _validate_job_handler_return(handler)
            self.handlers[job_type] = handler
            return handler

        return decorator


def _validate_job_handler_signature(handler: Callable[..., JobResult]) -> None:
    handler_signature = signature(handler)
    annotations = get_type_hints(handler)
    positional_parameters = [
        parameter
        for parameter in handler_signature.parameters.values()
        if parameter.kind
        in {
            parameter.POSITIONAL_ONLY,
            parameter.POSITIONAL_OR_KEYWORD,
        }
    ]
    required_parameters = [
        parameter
        for parameter in positional_parameters
        if parameter.default is Signature.empty
    ]
    if len(required_parameters) != 1:
        raise TypeError("Job handler must accept exactly one JobContext argument.")
    context_parameter = required_parameters[0]
    if annotations.get(context_parameter.name) is not JobContext:
        raise TypeError("Job handler must accept exactly one JobContext argument.")


def _validate_job_handler_return(handler: Callable[..., JobResult]) -> None:
    return_annotation = get_type_hints(handler).get("return")
    if return_annotation is JobResult:
        return

    raise TypeError("Job handler must return JobResult.")

