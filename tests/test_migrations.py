"""Tests for versioned, forward-only database migrations."""

import sqlite3
from pathlib import Path

import pytest
from flask import Flask

from task_manager import create_app
from task_manager.db import get_db
from task_manager.migrations import discover_migrations, upgrade_db
from task_manager.tasks import repository

LEGACY_SCHEMA = """
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK (is_completed IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_task_is_completed ON task (is_completed);
"""


def _legacy_app(tmp_path: Path) -> Flask:
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": tmp_path / "legacy.sqlite",
            "SECRET_KEY": "test",
        }
    )
    with app.app_context():
        get_db().executescript(LEGACY_SCHEMA)
    return app


def test_new_database_is_initialized_at_current_version(app: Flask) -> None:
    with app.app_context():
        migrations = discover_migrations()
        applied = (
            get_db()
            .execute("SELECT version FROM schema_migrations ORDER BY version")
            .fetchall()
        )

        assert [row["version"] for row in applied] == [
            migration.version for migration in migrations
        ]
        assert upgrade_db() == []


def test_upgrade_optimizes_listing_index_on_previous_database(tmp_path: Path) -> None:
    app = _legacy_app(tmp_path)

    with app.app_context():
        previous_index = (
            get_db()
            .execute(
                "SELECT name FROM sqlite_master WHERE type = 'index' AND name = ?",
                ("idx_task_is_completed",),
            )
            .fetchone()
        )

        applied = upgrade_db()
        indexes = {
            row["name"]
            for row in get_db().execute("PRAGMA index_list(task)").fetchall()
        }

        assert previous_index is not None
        assert applied == ["0001_optimize_task_listing"]
        assert "idx_task_listing" in indexes
        assert "idx_task_is_completed" not in indexes


def test_upgrade_preserves_existing_tasks_and_crud(tmp_path: Path) -> None:
    app = _legacy_app(tmp_path)
    with app.app_context():
        connection = get_db()
        connection.execute(
            """
            INSERT INTO task (
                id, title, description, is_completed, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (7, "Tarea conservada", "Datos previos", 1, "2026-01-02 03:04:05"),
        )
        connection.commit()

        upgrade_db()
        preserved = repository.get_task(7)
        new_id = repository.create_task("Tarea posterior")

        assert preserved is not None
        assert dict(preserved) == {
            "id": 7,
            "title": "Tarea conservada",
            "description": "Datos previos",
            "is_completed": 1,
            "created_at": preserved["created_at"],
            "updated_at": preserved["updated_at"],
        }
        assert str(preserved["created_at"]) == "2026-01-02 03:04:05"
        assert repository.update_task(new_id, "Tarea actualizada") is True
        assert repository.set_task_completed(new_id, True) is True
        assert repository.delete_task(new_id) is True

    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b"Tarea conservada" in response.data


def test_migrations_run_once_in_filename_order(app: Flask, tmp_path: Path) -> None:
    migration_dir = tmp_path / "migrations"
    migration_dir.mkdir()
    (migration_dir / "0002_second.sql").write_text(
        "INSERT INTO migration_order (name) VALUES ('second');",
        encoding="utf-8",
    )
    (migration_dir / "0001_first.sql").write_text(
        """
        CREATE TABLE migration_order (position INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO migration_order (name) VALUES ('first');
        """,
        encoding="utf-8",
    )

    with app.app_context():
        get_db().execute("DELETE FROM schema_migrations")
        get_db().commit()

        first_run = upgrade_db(migration_dir)
        second_run = upgrade_db(migration_dir)
        rows = (
            get_db()
            .execute("SELECT name FROM migration_order ORDER BY position")
            .fetchall()
        )
        recorded = (
            get_db()
            .execute("SELECT version FROM schema_migrations ORDER BY version")
            .fetchall()
        )

        assert first_run == ["0001_first", "0002_second"]
        assert second_run == []
        assert [row["name"] for row in rows] == ["first", "second"]
        assert [row["version"] for row in recorded] == first_run


def test_failed_migration_rolls_back_and_is_not_recorded(
    app: Flask, tmp_path: Path
) -> None:
    migration_dir = tmp_path / "migrations"
    migration_dir.mkdir()
    (migration_dir / "0001_broken.sql").write_text(
        """
        CREATE TABLE should_be_rolled_back (id INTEGER);
        INSERT INTO missing_table (id) VALUES (1);
        """,
        encoding="utf-8",
    )

    with app.app_context():
        with pytest.raises(sqlite3.OperationalError, match="missing_table"):
            upgrade_db(migration_dir)

        table = (
            get_db()
            .execute(
                """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = ?
            """,
                ("should_be_rolled_back",),
            )
            .fetchone()
        )
        recorded = (
            get_db()
            .execute(
                "SELECT version FROM schema_migrations WHERE version = ?",
                ("0001_broken",),
            )
            .fetchone()
        )

        assert table is None
        assert recorded is None


def test_upgrade_db_cli_is_idempotent(tmp_path: Path) -> None:
    app = _legacy_app(tmp_path)
    runner = app.test_cli_runner()

    first = runner.invoke(args=["upgrade-db"])
    second = runner.invoke(args=["upgrade-db"])

    assert first.exit_code == 0
    assert "Applied 1 migration(s): 0001_optimize_task_listing" in first.output
    assert second.exit_code == 0
    assert "Database is already up to date." in second.output


def test_init_db_then_upgrade_db_has_no_pending_migrations(tmp_path: Path) -> None:
    app = _legacy_app(tmp_path)
    runner = app.test_cli_runner()

    initialized = runner.invoke(args=["init-db"])
    upgraded = runner.invoke(args=["upgrade-db"])

    assert initialized.exit_code == 0
    assert "Initialized the database." in initialized.output
    assert upgraded.exit_code == 0
    assert "Database is already up to date." in upgraded.output

    with app.app_context():
        versions = get_db().execute("SELECT version FROM schema_migrations").fetchall()
        indexes = {
            row["name"]
            for row in get_db().execute("PRAGMA index_list(task)").fetchall()
        }

        assert [row["version"] for row in versions] == ["0001_optimize_task_listing"]
        assert "idx_task_listing" in indexes


@pytest.mark.parametrize(
    "filenames",
    [
        ("0001_first.sql", "0001_duplicate.sql"),
        ("0001_first.sql", "0003_gap.sql"),
    ],
)
def test_discovery_rejects_duplicate_or_missing_numbers(
    tmp_path: Path, filenames: tuple[str, str]
) -> None:
    migration_dir = tmp_path / "migrations"
    migration_dir.mkdir()
    for filename in filenames:
        (migration_dir / filename).write_text("SELECT 1;", encoding="utf-8")

    with pytest.raises(RuntimeError, match="unique and consecutive"):
        discover_migrations(migration_dir)
