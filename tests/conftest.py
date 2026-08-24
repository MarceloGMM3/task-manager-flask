import re
from collections.abc import Callable, Iterator
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


@pytest.fixture
def csrf_token(client: FlaskClient) -> Callable[[str], str]:
    """Return a helper that obtains a genuine CSRF token from a form."""

    def get_token(path: str = "/tasks/create") -> str:
        response = client.get(path)
        match = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', response.data)
        if match is None:
            raise AssertionError("Rendered form did not contain a CSRF token")
        return match.group(1).decode()

    return get_token
