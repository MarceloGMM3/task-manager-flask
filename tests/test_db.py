import sqlite3

import pytest
from flask import Flask

from task_manager.db import get_db


def test_get_db_reuses_connection_within_context(app: Flask) -> None:
    with app.app_context():
        first_connection = get_db()
        second_connection = get_db()

        assert first_connection is second_connection
        assert first_connection.row_factory is sqlite3.Row
        foreign_keys_enabled = first_connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

        assert foreign_keys_enabled == 1


def test_connection_closes_after_application_context(app: Flask) -> None:
    with app.app_context():
        connection = get_db()

    with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
        connection.execute("SELECT 1")


def test_init_db_command_creates_task_table(app: Flask) -> None:
    result = app.test_cli_runner().invoke(args=["init-db"])

    assert result.exit_code == 0
    assert "Initialized the database." in result.output

    with app.app_context():
        table = (
            get_db()
            .execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'task'"
            )
            .fetchone()
        )
        columns = get_db().execute("PRAGMA table_info(task)").fetchall()

        assert table["name"] == "task"
        assert {column["name"] for column in columns} == {
            "id",
            "title",
            "description",
            "is_completed",
            "created_at",
            "updated_at",
        }
