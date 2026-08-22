from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from task_manager import create_app
from task_manager.db import init_db


@pytest.fixture
def app(tmp_path: Path) -> Iterator[Flask]:
    database_path = tmp_path / "test.sqlite"
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": database_path,
            "SECRET_KEY": "test",
        }
    )

    with application.app_context():
        init_db()

    yield application


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
