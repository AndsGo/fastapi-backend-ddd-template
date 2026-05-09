from typing import Any

from app.application.errors import NotFoundError
from app.application.ports import ExampleItemRepositoryPort


class GetExampleItemUseCase:
    def __init__(self, repository: ExampleItemRepositoryPort) -> None:
        self.repository = repository

    def execute(self, item_id: int) -> Any:
        item = self.repository.get(item_id)
        if item is None:
            raise NotFoundError("example_item", item_id)
        return item
