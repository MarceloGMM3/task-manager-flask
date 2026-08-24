"""HTTP routes for task management."""

from flask import abort, flash, redirect, render_template, request, url_for

from task_manager.tasks import bp, repository


@bp.get("/")
def index() -> str:
    """Render the task list."""
    return render_template("tasks/index.html", tasks=repository.list_tasks())


@bp.route("/tasks/create", methods=("GET", "POST"))
def create() -> str:
    """Create a task from form input."""
    if request.method == "POST":
        title, description = _task_form_values()
        if not title:
            flash("El título es obligatorio.", "error")
            return render_template("tasks/form.html", task=None), 400

        repository.create_task(title, description)
        flash("Tarea creada correctamente.", "success")
        return redirect(url_for("tasks.index"))

    return render_template("tasks/form.html", task=None)


@bp.route("/tasks/<int:task_id>/edit", methods=("GET", "POST"))
def edit(task_id: int) -> str:
    """Edit an existing task."""
    task = _get_task_or_404(task_id)
    if request.method == "POST":
        title, description = _task_form_values()
        if not title:
            flash("El título es obligatorio.", "error")
            return render_template("tasks/form.html", task=task), 400

        repository.update_task(task_id, title, description)
        flash("Tarea actualizada correctamente.", "success")
        return redirect(url_for("tasks.index"))

    return render_template("tasks/form.html", task=task)


@bp.post("/tasks/<int:task_id>/toggle")
def toggle(task_id: int) -> str:
    """Toggle an existing task's completion state."""
    task = _get_task_or_404(task_id)
    repository.set_task_completed(task_id, not bool(task["is_completed"]))
    return redirect(url_for("tasks.index"))


@bp.post("/tasks/<int:task_id>/delete")
def delete(task_id: int) -> str:
    """Delete an existing task."""
    _get_task_or_404(task_id)
    repository.delete_task(task_id)
    flash("Tarea eliminada.", "success")
    return redirect(url_for("tasks.index"))


def _get_task_or_404(task_id: int):
    task = repository.get_task(task_id)
    if task is None:
        abort(404)
    return task


def _task_form_values() -> tuple[str, str]:
    return request.form.get("title", "").strip(), request.form.get(
        "description", ""
    ).strip()
