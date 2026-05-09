from pathlib import Path

REMOVED_LEGACY_PATHS = [
    "app/api",
    "app/schemas",
    "app/db",
    "app/models",
    "app/repositories",
    "app/cache",
    "app/jobs",
    "app/domains",
    "app/core",
    "app/core/config.py",
    "app/core/logging.py",
    "tests/compatibility",
    "docs/compatibility-deletion-inventory.md",
]

REMOVED_LEGACY_MODULES = [
    "app." + module
    for module in [
        "api",
        "schemas",
        "db",
        "models",
        "repositories",
        "cache",
        "jobs",
        "domains",
        "core",
        "core.config",
        "core.logging",
    ]
]


def test_application_does_not_import_http_schemas() -> None:
    root = Path(__file__).resolve().parents[1]
    checked_files = [
        *Path(root, "app", "application").rglob("*.py"),
    ]

    offenders = [
        path.relative_to(root).as_posix()
        for path in checked_files
        if ("from app." + "schemas") in path.read_text(encoding="utf-8")
        or ("from app.interface.http." + "schemas") in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_http_schemas_do_not_import_application_dtos() -> None:
    root = Path(__file__).resolve().parents[1]
    checked_files = Path(root, "app", "interface", "http", "schemas").rglob("*.py")

    offenders = [
        path.relative_to(root).as_posix()
        for path in checked_files
        if "from app.application.dto" in path.read_text(encoding="utf-8")
        or "import app.application.dto" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_only_composition_roots_import_infrastructure_from_interface() -> None:
    root = Path(__file__).resolve().parents[1]
    allowed_files = {
        Path(root, "app", "interface", "http", "v1", "providers.py").resolve(),
        Path(root, "app", "interface", "jobs", "runner.py").resolve(),
    }
    checked_files = [
        path
        for path in Path(root, "app", "interface").rglob("*.py")
        if path.resolve() not in allowed_files
    ]

    offenders = [
        path.relative_to(root).as_posix()
        for path in checked_files
        if "from app.infrastructure" in path.read_text(encoding="utf-8")
        or "import app.infrastructure" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_environment_variables_are_read_only_in_settings() -> None:
    root = Path(__file__).resolve().parents[1]
    allowed_file = Path(root, "app", "config", "settings.py").resolve()
    checked_files = [
        path
        for path in Path(root, "app").rglob("*.py")
        if path.resolve() != allowed_file
    ]

    offenders = [
        path.relative_to(root).as_posix()
        for path in checked_files
        if any(
            pattern in path.read_text(encoding="utf-8")
            for pattern in ("os.environ", "os.getenv", "environ[")
        )
    ]

    assert offenders == []


def test_strict_ddd_runtime_services_layer_is_removed() -> None:
    root = Path(__file__).resolve().parents[1]

    assert not Path(root, "app", "services").exists()


def test_application_use_cases_do_not_import_services() -> None:
    root = Path(__file__).resolve().parents[1]
    checked_files = Path(root, "app", "application").rglob("*.py")

    offenders = [
        path.relative_to(root).as_posix()
        for path in checked_files
        if "from app.services" in path.read_text(encoding="utf-8")
        or "import app.services" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_legacy_wrapper_paths_are_removed() -> None:
    root = Path(__file__).resolve().parents[1]

    existing_paths = [
        removed_path
        for removed_path in REMOVED_LEGACY_PATHS
        if Path(root, removed_path).exists()
    ]

    assert existing_paths == []


def test_active_code_does_not_reference_removed_legacy_imports() -> None:
    root = Path(__file__).resolve().parents[1]
    current_test = Path(__file__).resolve()
    checked_files = [
        path
        for base in [Path(root, "app"), Path(root, "tests")]
        for path in base.rglob("*.py")
        if path.resolve() != current_test
    ]

    offenders = {}
    for path in checked_files:
        text = path.read_text(encoding="utf-8")
        legacy_references = []
        for module in REMOVED_LEGACY_MODULES:
            suffix = module.removeprefix("app.")
            parent_module, _, imported_name = suffix.rpartition(".")
            import_from_app = (
                f"from app import {suffix}"
                if not parent_module
                else f"from app.{parent_module} import {imported_name}"
            )
            legacy_references.extend(
                reference
                for reference in (
                    import_from_app,
                    f"from {module}",
                    f"import {module}",
                    f'import_module("{module}',
                    f"import_module('{module}",
                    f'__import__("{module}")',
                    f"__import__('{module}')",
                )
                if reference in text
            )
        if legacy_references:
            offenders[path.relative_to(root).as_posix()] = legacy_references

    assert offenders == {}
