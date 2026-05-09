from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

import app.infrastructure.persistence.models  # noqa: F401
from app.infrastructure.database.base import Base

MIGRATIONS_DIR = Path("app/infrastructure/persistence/migrations/versions")


def test_template_migration_chain_has_single_initial_revision() -> None:
    migrations = sorted(MIGRATIONS_DIR.glob("*.py"))

    assert [path.name for path in migrations] == [
        "20260508_0001_create_framework_template_tables.py"
    ]


def test_alembic_script_location_uses_infrastructure_migrations() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    assert Path(script.dir).as_posix().endswith(
        "app/infrastructure/persistence/migrations",
    )
    assert script.get_revision("20260508_0001") is not None


def test_alembic_uses_explicit_path_separator() -> None:
    config = Config("alembic.ini")

    assert config.get_main_option("path_separator") == "os"


def test_target_metadata_includes_framework_tables_for_autogenerate() -> None:
    assert {
        "audit_logs",
        "example_items",
        "scheduled_jobs",
        "scheduled_job_runs",
    }.issubset(Base.metadata.tables)


def test_initial_template_migration_creates_framework_tables_only() -> None:
    migration_text = MIGRATIONS_DIR.joinpath(
        "20260508_0001_create_framework_template_tables.py",
    ).read_text(encoding="utf-8")

    expected_tables = [
        '"audit_logs"',
        '"example_items"',
        '"scheduled_jobs"',
        '"scheduled_job_runs"',
    ]
    forbidden_tokens = [
        "list" + "ings",
        "prod" + "ucts",
        "chan" + "nels",
        "market" + "place",
    ]

    for table in expected_tables:
        assert table in migration_text
    for token in forbidden_tokens:
        assert token not in migration_text


def test_migrations_do_not_use_postgresql_only_types() -> None:
    forbidden_tokens = [
        "postgresql.JSONB",
        "postgresql.ARRAY",
        "postgresql.UUID",
        "from sqlalchemy.dialects import postgresql",
    ]
    migration_text = "\n".join(
        path.read_text(encoding="utf-8") for path in MIGRATIONS_DIR.glob("*.py")
    )

    for token in forbidden_tokens:
        assert token not in migration_text


def test_initial_migration_declares_mysql_binary_collation_for_business_keys() -> None:
    migration_text = MIGRATIONS_DIR.joinpath(
        "20260508_0001_create_framework_template_tables.py",
    ).read_text(encoding="utf-8")

    assert "utf8mb4_bin" in migration_text
    assert "_case_sensitive_string(64)" in migration_text
    assert "_case_sensitive_string(128)" in migration_text
