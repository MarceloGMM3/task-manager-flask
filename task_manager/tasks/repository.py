"""Persistence operations for tasks."""

import sqlite3
from collections.abc import Sequence

from task_manager.db import get_db


def list_tasks() -> list[sqlite3.Row]:
    """Return all tasks, with pending tasks first."""
    return (
        get_db()
        .execute(
            """
        SELECT id, title, description, is_completed, created_at, updated_at
        FROM task
        ORDER BY is_completed ASC, created_at DESC, id DESC
        """
        )
        .fetchall()
    )


def get_task(task_id: int) -> sqlite3.Row | None:
    """Return a task by identifier, or None when it does not exist."""
    return (
        get_db()
        .execute(
            """
        SELECT id, title, description, is_completed, created_at, updated_at
        FROM task
        WHERE id = ?
        """,
            (task_id,),
        )
        .fetchone()
    )


def create_task(title: str, description: str = "") -> int:
    """Create a task and return its identifier."""
    title = _normalize_title(title)
    cursor = _execute_write(
        "INSERT INTO task (title, description) VALUES (?, ?)",
        (title, description),
    )
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not return an identifier for the new task")
    return cursor.lastrowid


def update_task(task_id: int, title: str, description: str = "") -> bool:
    """Update a task and report whether it existed."""
    title = _normalize_title(title)
    cursor = _execute_write(
        """
        UPDATE task
        SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (title, description, task_id),
    )
    return cursor.rowcount > 0


def set_task_completed(task_id: int, is_completed: bool) -> bool:
    """Set a task's completion state and report whether it existed."""
    cursor = _execute_write(
        """
        UPDATE task
        SET is_completed = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (int(is_completed), task_id),
    )
    return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    """Delete a task and report whether it existed."""
    cursor = _execute_write("DELETE FROM task WHERE id = ?", (task_id,))
    return cursor.rowcount > 0


def _normalize_title(title: str) -> str:
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("Task title is required")
    return normalized_title


def _execute_write(sql: str, parameters: Sequence[object]) -> sqlite3.Cursor:
    """Execute and commit one write, rolling it back if SQLite rejects it."""
    connection = get_db()
    try:
        cursor = connection.execute(sql, parameters)
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    return cursor
