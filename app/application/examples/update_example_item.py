from typing import Any

from app.application.dto.example import UpdateExampleItemCommand
from app.application.errors import NotFoundError
from app.application.ports import ExampleItemRepositoryPort


class UpdateExampleItemUseCase:
    def __init__(self, repository: ExampleItemRepositoryPort) -> None:
        self.repository = repository

    def execute(self, item_id: int, command: UpdateExampleItemCommand) -> Any:
        item = self.repository.get(item_id)
        if item is None:
            raise NotFoundError("example_item", item_id)
        return self.repository.update(item, command.model_dump(exclude_unset=True))
