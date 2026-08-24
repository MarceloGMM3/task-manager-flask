"""Application error handlers."""

from flask import Flask, render_template
from werkzeug.exceptions import InternalServerError, NotFound


def register_error_handlers(app: Flask) -> None:
    """Register HTML responses for common application errors."""

    @app.errorhandler(404)
    def not_found(error: NotFound) -> tuple[str, int]:
        return render_template("errors/404.html"), error.code

    @app.errorhandler(500)
    def internal_server_error(error: InternalServerError) -> tuple[str, int]:
        return render_template("errors/500.html"), error.code
