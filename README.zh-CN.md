# FastAPI 后端模板

这是一个可复用的纯后端 FastAPI 项目模板，适合作为严格 DDD 风格模块化单体服务的基础工程。

[English README](README.md)

## 项目包含

- FastAPI API 版本管理和依赖注入。
- SQLAlchemy 模型、仓储、会话管理和 Alembic 数据库迁移。
- 通过 `DATABASE_URL` 支持 PostgreSQL 和 MySQL。
- Redis 客户端和统一的 Redis key 模板。
- 定时任务定义、调度器、并发 worker 和任务注册表。
- 输出到 stdout 的 JSON 日志，以及可选的本地滚动日志文件。
- 严格 DDD 风格的 interface、application、domain、ports、infrastructure 分层。
- 一个 `examples` 示例模块，用于展示推荐的代码组织方式。

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

编辑 `.env`，至少确认 `DATABASE_URL` 指向你的数据库。Redis 是可选的，除非你要运行分布式任务或使用 Redis 缓存能力。

`app/config` 是唯一配置包。环境变量通过 `app/config/settings.py` 读取，并通过 `app.config` 暴露。

## 运行

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

启动后打开：

```text
http://127.0.0.1:8000/docs
```

## 运行定时任务

```bash
python -m app.interface.jobs.runner scheduler --interval-seconds 10
python -m app.interface.jobs.runner worker --interval-seconds 5 --worker-id worker-1 --max-workers 4
```

也可以使用安装后的命令行入口：

```bash
backend-jobs worker --once --max-workers 4
```

## 验证项目

```bash
python -m pytest
python -m ruff check .
python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
python -m mypy app
```

GitHub Actions 和 GitLab CI 都会运行同一组 gate。GitLab 使用仓库根目录的 `.gitlab-ci.yml`。

## 作为模板使用

新增业务模块时，参考现有 `examples` 模块：

- 在 `app/domain` 中新增框架无关的枚举、值对象和领域策略。
- 在 `app/application/ports` 中新增 repository 或 gateway 协议。
- 在 `app/application/dto` 和 `app/application/<module>` 中新增 DTO 和用例。
- 在 `app/infrastructure/persistence/models` 中新增数据库模型。
- 在 `app/infrastructure/persistence/repositories` 中封装数据库访问。
- 在 `app/interface/http/schemas` 中新增 HTTP 请求和响应 schema。
- 在 `app/interface/http/v1/endpoints` 中暴露 HTTP 接口，并注册到 `app/interface/http/v1/router.py`。
- 在 `app/interface/http/v1/providers.py` 或相关 job composition root 中把基础设施实现注入 application use case。
- 在 `tests` 中补充 repository、application use case 和 endpoint 测试。
- 根据变更同步更新 `docs` 下的相关文档。

`app/application/ports` 属于 application 层。Port 描述 use case 需要的外部能力，infrastructure repository 或 gateway 是满足这些协议的 adapter。Application use case 只能依赖 port 协议，不能直接依赖具体 SQLAlchemy repository、Redis client 或其他基础设施实现。

HTTP schema 和 application DTO 是不同层的契约。Endpoint 在调用 use case 前负责把 request schema 转换成 application command/query DTO。

接口层应保持轻量。用例编排放在 `app/application`，纯业务规则放在 `app/domain`，数据库查询放在 repository 层。运行时代码不再使用 `app/services`。

## Domain Layer

`app/domain` 是纯业务枚举、值对象和策略的 canonical package。

Domain policy functions must be deterministic and framework-free. They may return domain enum/value-object decisions, but must not import FastAPI, SQLAlchemy, Pydantic, Redis, repositories, services, infrastructure, interface adapters, config, or application modules.

## 认证和权限

当前项目只保留认证和权限的占位设计。正式用于生产项目前，需要先确认目标方案，例如 SSO、OAuth2、JWT、RBAC 或其他组织内统一认证体系。

## 主要文档

- [架构说明](docs/architecture.md)
- [DDD 快速入门](docs/ddd-quickstart.md)
- [开发指南](docs/development-guide.md)
- [数据库设计](docs/database-design.md)
- [任务系统指南](docs/job-guide.md)
- [项目框架规范](docs/project-framework-standards.md)
- [认证与安全占位说明](docs/security-and-auth-placeholder.md)
