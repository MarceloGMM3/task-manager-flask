"""Task management blueprint."""

from flask import Blueprint

bp = Blueprint("tasks", __name__)

from task_manager.tasks import routes  # noqa: E402, F401
