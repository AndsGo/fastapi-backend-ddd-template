from typing import Any

from app.application.dto.example import CreateExampleItemCommand
from app.application.errors import ConflictError
from app.application.ports import ExampleItemRepositoryPort


class CreateExampleItemUseCase:
    def __init__(self, repository: ExampleItemRepositoryPort) -> None:
        self.repository = repository

    def execute(self, command: CreateExampleItemCommand) -> Any:
        if self.repository.get_by_code(command.code) is not None:
            raise ConflictError("example_item", "code already exists")
        return self.repository.create(command.model_dump())
