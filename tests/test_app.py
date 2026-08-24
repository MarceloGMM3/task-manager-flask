import pytest
from flask import Flask

from task_manager import create_app


def test_create_app() -> None:
    app = create_app({"TESTING": True})

    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True
    assert app.config["APP_ENV"] == "development"


def test_test_config_overrides_defaults() -> None:
    app = create_app({"SECRET_KEY": "overridden-for-test"})

    assert app.config["SECRET_KEY"] == "overridden-for-test"


def test_production_accepts_secure_secret_key() -> None:
    app = create_app(
        {
            "APP_ENV": "production",
            "SECRET_KEY": "a-secure-production-secret",
        }
    )

    assert app.config["APP_ENV"] == "production"
    assert app.config["SECRET_KEY"] == "a-secure-production-secret"


@pytest.mark.parametrize("secret_key", [None, "", "   ", "dev", " dev "])
def test_production_rejects_missing_or_insecure_secret_key(
    secret_key: str | None,
) -> None:
    with pytest.raises(RuntimeError, match="A secure SECRET_KEY is required"):
        create_app({"APP_ENV": "production", "SECRET_KEY": secret_key})
