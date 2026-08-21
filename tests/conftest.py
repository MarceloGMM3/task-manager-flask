from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask

from task_manager import create_app


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

    yield application
