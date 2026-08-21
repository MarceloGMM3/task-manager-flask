"""Application factory for the task manager."""

from pathlib import Path

from flask import Flask

from task_manager.config import Config
from task_manager.db import init_app as init_db_app


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    """Create and configure a Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.from_mapping(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_db_app(app)

    return app
