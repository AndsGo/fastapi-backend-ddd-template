# DDD Quickstart

这份文档给还不熟悉 DDD 架构的同学使用。目标不是解释完整 DDD 理论，而是让你能在这个项目里快速找到代码应该放在哪里，并避免破坏架构边界。

## 先记住一条主线

一次 HTTP 请求的大致流向是：

```text
HTTP endpoint
  -> application use case
  -> application port
  -> infrastructure repository
  -> persistence model
  -> database
```

对应目录是：

```text
app/interface/http       # HTTP endpoint、schema、依赖注入
app/application          # use case、DTO、ports、应用异常
app/domain               # 纯业务枚举、值对象、策略
app/infrastructure       # SQLAlchemy、Redis、jobs、logging 等技术实现
app/config               # 配置和环境变量读取
app/shared               # 稳定的跨层基础对象
```

这个项目没有运行时 `app/services` 层。简单业务流程放在 application use case；纯业务规则放在 domain。

## 每层做什么

`app/interface/http`

- 接收 HTTP 请求。
- 使用 HTTP schema 做请求和响应契约。
- 把 HTTP schema 转换成 application DTO。
- 通过 provider 拿到 use case。
- 不直接查数据库，不直接调用 repository。

`app/application`

- 定义一次业务动作，例如创建、更新、查询。
- 编排 use case 流程。
- 使用 `app/application/dto` 作为非 HTTP DTO。
- 使用 `app/application/ports` 描述需要的外部能力。
- 不 import `app/infrastructure`，不 import `app/interface`。

`app/application/ports`

- 定义 use case 需要什么能力。
- 只写协议，不写 SQLAlchemy 查询。
- 不能依赖 FastAPI、SQLAlchemy、Redis、Pydantic、config、interface、infrastructure 或 application DTO。

可以把 port 理解成：

```text
application 对外部世界提出的能力需求
```

例如：use case 需要“根据 code 查 ExampleItem”和“创建 ExampleItem”，就定义 repository port。具体怎么查数据库，是 infrastructure repository 的事。

`app/domain`

- 放纯业务语言。
- 适合放枚举、值对象、确定性策略、领域规则。
- 不依赖 FastAPI、SQLAlchemy、Pydantic、Redis、repository、application、interface、infrastructure、config。

`app/infrastructure`

- 放技术实现。
- SQLAlchemy model 在 `app/infrastructure/persistence/models`。
- SQLAlchemy repository 在 `app/infrastructure/persistence/repositories`。
- Redis、jobs、logging、database session 都在这里。
- repository 可以实现 application port，但不能依赖 use case 或 DTO。

## 新增一个模块时怎么做

假设要新增一个 `orders` 模块，推荐按这个顺序做。

### 1. 先放纯业务规则

如果有业务状态、策略或值对象，放到：

```text
app/domain/orders/
```

示例：

```python
from enum import StrEnum


class OrderStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
```

如果只是普通 CRUD，没有明确业务规则，可以先不新增 domain 文件。

### 2. 定义 application DTO

放到：

```text
app/application/dto/order.py
```

示例：

```python
from pydantic import BaseModel, Field


class CreateOrderCommand(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    customer_name: str = Field(min_length=1, max_length=128)
```

注意：application DTO 不是 HTTP schema。HTTP schema 放 interface 层，endpoint 负责转换。

### 3. 定义 port

放到：

```text
app/application/ports/repositories.py
```

示例：

```python
from typing import Any, Protocol


class OrderRepositoryPort(Protocol):
    def get_by_code(self, code: str) -> Any | None: ...

    def create(self, payload: dict[str, Any]) -> Any: ...
```

Port 只描述 use case 需要的方法。不要把 SQLAlchemy session、model、query 暴露给 application。

### 4. 写 use case

放到：

```text
app/application/orders/create_order.py
```

示例：

```python
from typing import Any

from app.application.dto.order import CreateOrderCommand
from app.application.errors import ConflictError
from app.application.ports import OrderRepositoryPort


class CreateOrderUseCase:
    def __init__(self, repository: OrderRepositoryPort) -> None:
        self.repository = repository

    def execute(self, command: CreateOrderCommand) -> Any:
        if self.repository.get_by_code(command.code) is not None:
            raise ConflictError("order", "code already exists")
        return self.repository.create(command.model_dump())
```

这里 use case 只依赖 DTO、errors、ports。它不知道 SQLAlchemy repository 的存在。

### 5. 写 persistence model

放到：

```text
app/infrastructure/persistence/models/order.py
```

Model 只描述数据库表，不写业务流程。

### 6. 写 repository adapter

放到：

```text
app/infrastructure/persistence/repositories/order_repository.py
```

Repository 负责 SQLAlchemy 查询，并满足 application port。

示例：

```python
from sqlalchemy import select

from app.infrastructure.persistence.models.order import Order
from app.infrastructure.persistence.repositories.base import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository[Order]):
    model = Order

    def get_by_code(self, code: str) -> Order | None:
        statement = select(Order).where(Order.code == code)
        return self.db.scalar(statement)
```

### 7. 写 HTTP schema

放到：

```text
app/interface/http/schemas/order.py
```

示例：

```python
from pydantic import BaseModel, Field

from app.interface.http.schemas.common import TimestampedResponse


class OrderCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    customer_name: str = Field(min_length=1, max_length=128)


class OrderResponse(TimestampedResponse):
    code: str
    customer_name: str
```

HTTP schema 不要继承 application DTO，也不要 import `app.application.dto`。

### 8. 写 provider 组装依赖

放到：

```text
app/interface/http/v1/providers.py
```

示例：

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.orders.create_order import CreateOrderUseCase
from app.infrastructure.database.session import get_db
from app.infrastructure.persistence.repositories.order_repository import OrderRepository


def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)


def get_create_order_use_case(
    repository: OrderRepository = Depends(get_order_repository),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(repository)
```

`providers.py` 是 HTTP composition root，允许 import infrastructure。

### 9. 写 endpoint

放到：

```text
app/interface/http/v1/endpoints/orders.py
```

示例：

```python
from typing import Any

from fastapi import APIRouter, Depends

from app.application.dto.order import CreateOrderCommand
from app.application.orders.create_order import CreateOrderUseCase
from app.interface.http.schemas.order import OrderCreate, OrderResponse
from app.interface.http.v1.providers import get_create_order_use_case

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    payload: OrderCreate,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> Any:
    command = CreateOrderCommand(**payload.model_dump())
    return use_case.execute(command)
```

Endpoint 可以 import application DTO，因为它负责把 HTTP schema 转成 use case DTO。

### 10. 注册路由

在：

```text
app/interface/http/v1/router.py
```

注册新 endpoint。

### 11. 写测试

至少补这些测试：

- application use case 测试：用 fake repository，不连数据库。
- repository 测试：检查 SQLAlchemy 查询或持久化行为。
- endpoint 测试：覆盖路由、请求 schema、响应。
- 架构门禁：通常已有通用测试会自动覆盖。

## 常见问题

### Endpoint 能不能直接查数据库？

不能。Endpoint 是 delivery adapter，只负责 HTTP 协议和调用 use case。

正确方式：

```text
endpoint -> use case -> port -> repository
```

### Use case 能不能 import repository？

不能。Use case 只能依赖 port。

错误：

```python
from app.infrastructure.persistence.repositories.order_repository import OrderRepository
```

正确：

```python
from app.application.ports import OrderRepositoryPort
```

### 为什么不直接用 repository，非要 port？

Port 让 application 定义自己需要什么能力，infrastructure 去适配这个能力。这样 use case 不会被 SQLAlchemy、Redis、外部 API 等技术细节绑死。

### HTTP schema 能不能继承 application DTO？

不能。HTTP schema 是接口契约，application DTO 是用例契约。它们属于不同层。

Endpoint 负责转换：

```python
command = CreateOrderCommand(**payload.model_dump())
```

### Domain 能不能用 Pydantic？

不能。Domain 要保持纯业务代码。需要校验请求数据时，用 HTTP schema；需要 use case DTO 时，用 application DTO。

### 配置在哪里读？

只在：

```text
app/config/settings.py
```

读取环境变量。其他代码从 `app.config` 导入 settings。

## 提交前检查

提交前运行：

```bash
python -m ruff check .
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
python -m mypy app
python -m pytest
```

如果 Import Linter 失败，优先看是不是依赖方向错了。常见原因是：

- application import 了 infrastructure。
- domain import 了框架或 application。
- HTTP schema import 了 application DTO。
- endpoint 之外的 interface 文件 import 了 infrastructure。
- repository import 了 DTO 或 use case。

## 最小心智模型

记住这句话：

```text
interface 适配外部请求，application 编排用例，domain 表达业务规则，infrastructure 实现技术细节。
```

再记住这句话：

```text
内层定义需要什么，外层负责怎么实现。
```
