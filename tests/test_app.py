from flask import Flask

from task_manager import create_app


def test_create_app() -> None:
    app = create_app({"TESTING": True})

    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True


def test_test_config_overrides_defaults() -> None:
    app = create_app({"SECRET_KEY": "overridden-for-test"})

    assert app.config["SECRET_KEY"] == "overridden-for-test"
