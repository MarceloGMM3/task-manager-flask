"""Application factory for the task manager."""

from pathlib import Path

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from task_manager.config import Config
from task_manager.db import init_app as init_db_app
from task_manager.errors import register_error_handlers
from task_manager.tasks import bp as tasks_bp

csrf = CSRFProtect()


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    """Create and configure a Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.from_mapping(test_config)

    _validate_security_config(app)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    csrf.init_app(app)
    init_db_app(app)
    app.register_blueprint(tasks_bp)
    register_error_handlers(app)

    return app


def _validate_security_config(app: Flask) -> None:
    """Reject unsafe secret keys when production is explicitly selected."""
    if app.config["APP_ENV"] != "production":
        return

    secret_key = app.config.get("SECRET_KEY")
    if (
        not isinstance(secret_key, str)
        or not secret_key.strip()
        or secret_key.strip() == "dev"
    ):
        raise RuntimeError(
            "A secure SECRET_KEY is required when APP_ENV is set to production"
        )
