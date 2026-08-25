"""Small, explicit, forward-only SQLite migration runner."""

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import click
from flask import Flask
from flask.cli import with_appcontext

from task_manager.db import get_db

MIGRATION_FILENAME = re.compile(r"^(?P<version>\d{4}_[a-z0-9_]+)\.sql$")


@dataclass(frozen=True)
class Migration:
    """One ordered SQL migration stored on disk."""

    number: int
    version: str
    path: Path


def discover_migrations(directory: Path | None = None) -> list[Migration]:
    """Return valid migration files ordered by their versioned filename."""
    migration_directory = directory or Path(__file__).with_name("migrations")
    migrations = []
    for path in migration_directory.glob("*.sql"):
        match = MIGRATION_FILENAME.fullmatch(path.name)
        if match is None:
            raise RuntimeError(f"Invalid migration filename: {path.name}")
        version = match.group("version")
        migrations.append(Migration(int(version[:4]), version, path))

    migrations.sort(key=lambda migration: migration.number)
    numbers = [migration.number for migration in migrations]
    if numbers != list(range(1, len(migrations) + 1)):
        raise RuntimeError(
            "Migration numbers must be unique and consecutive starting at 0001"
        )
    return migrations


def upgrade_db(directory: Path | None = None) -> list[str]:
    """Apply pending migrations atomically and return their versions."""
    connection = get_db()
    _ensure_migration_table(connection)
    applied = {
        row["version"]
        for row in connection.execute("SELECT version FROM schema_migrations")
    }
    applied_now = []

    for migration in discover_migrations(directory):
        if migration.version in applied:
            continue
        _apply_migration(connection, migration)
        applied_now.append(migration.version)

    return applied_now


def _ensure_migration_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()


def _apply_migration(connection: sqlite3.Connection, migration: Migration) -> None:
    sql = migration.path.read_text(encoding="utf-8")
    statements = _sql_statements(sql)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO schema_migrations (version) VALUES (?)",
            (migration.version,),
        )
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise


def _sql_statements(sql: str) -> list[str]:
    """Split trusted migration SQL using SQLite's completeness parser."""
    statements = []
    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            if buffer.strip():
                statements.append(buffer)
            buffer = ""
    if buffer.strip():
        raise RuntimeError("Migration contains an incomplete SQL statement")
    return statements


@click.command("upgrade-db")
@with_appcontext
def upgrade_db_command() -> None:
    """Upgrade the configured database with all pending migrations."""
    applied = upgrade_db()
    if applied:
        click.echo(f"Applied {len(applied)} migration(s): {', '.join(applied)}")
    else:
        click.echo("Database is already up to date.")


def init_app(app: Flask) -> None:
    """Register migration commands on the application."""
    app.cli.add_command(upgrade_db_command)
