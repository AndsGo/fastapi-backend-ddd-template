from datetime import UTC, datetime
from types import SimpleNamespace

from app.application.dto.example import CreateExampleItemCommand, UpdateExampleItemCommand
from app.application.examples.create_example_item import CreateExampleItemUseCase
from app.application.examples.get_example_item import GetExampleItemUseCase
from app.application.examples.list_example_items import ListExampleItemsUseCase
from app.application.examples.update_example_item import UpdateExampleItemUseCase


class FakeExampleRepository:
    def __init__(self) -> None:
        self.created_payload: dict[str, object] | None = None
        self.updated_payload: dict[str, object] | None = None
        self.items = {
            1: SimpleNamespace(
                id=1,
                code="sample",
                name="Sample",
                description=None,
                created_at=datetime.now(UTC),
                updated_at=None,
            )
        }

    def list(self, skip: int = 0, limit: int = 100) -> list[object]:
        return list(self.items.values())[skip : skip + limit]

    def get(self, resource_id: int) -> object | None:
        return self.items.get(resource_id)

    def get_by_code(self, code: str) -> object | None:
        return next((item for item in self.items.values() if item.code == code), None)

    def create(self, payload: dict[str, object]) -> object:
        self.created_payload = payload
        item = SimpleNamespace(
            id=2,
            created_at=datetime.now(UTC),
            updated_at=None,
            **payload,
        )
        self.items[item.id] = item
        return item

    def update(self, entity: object, payload: dict[str, object]) -> object:
        self.updated_payload = payload
        for key, value in payload.items():
            setattr(entity, key, value)
        return entity


def test_create_example_item_use_case_maps_command_to_repository_payload() -> None:
    repository = FakeExampleRepository()

    item = CreateExampleItemUseCase(repository).execute(
        CreateExampleItemCommand(code="new-code", name="New Item"),
    )

    assert repository.created_payload == {
        "code": "new-code",
        "name": "New Item",
        "description": None,
    }
    assert item.code == "new-code"


def test_list_example_items_use_case_delegates_to_repository() -> None:
    items = ListExampleItemsUseCase(FakeExampleRepository()).execute(skip=0, limit=10)

    assert len(items) == 1


def test_get_example_item_use_case_delegates_to_repository() -> None:
    item = GetExampleItemUseCase(FakeExampleRepository()).execute(1)

    assert item.id == 1


def test_update_example_item_use_case_maps_command_to_repository_payload() -> None:
    repository = FakeExampleRepository()

    item = UpdateExampleItemUseCase(repository).execute(
        1,
        UpdateExampleItemCommand(name="Renamed"),
    )

    assert repository.updated_payload == {"name": "Renamed"}
    assert item.name == "Renamed"
