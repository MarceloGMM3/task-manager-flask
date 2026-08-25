"""SQLite connection and schema initialization helpers."""

import sqlite3
from pathlib import Path

import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext


def get_db() -> sqlite3.Connection:
    """Return the SQLite connection for the current application context."""
    if "db" not in g:
        database = current_app.config.get("DATABASE")
        if database is None:
            database = Path(current_app.instance_path) / "task_manager.sqlite"

        g.db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(error: BaseException | None = None) -> None:
    """Close the current context's database connection, if one exists."""
    del error
    connection = g.pop("db", None)

    if connection is not None:
        connection.close()


def init_db() -> None:
    """Destructively create the current schema declared in schema.sql."""
    schema_path = Path(__file__).with_name("schema.sql")
    get_db().executescript(schema_path.read_text(encoding="utf-8"))


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """Initialize or reset the configured development database."""
    init_db()
    click.echo("Initialized the database. Existing data was reset.")


def init_app(app: Flask) -> None:
    """Register database lifecycle hooks and commands on the app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
