import pytest
from flask import Flask

from task_manager.tasks import repository


def test_create_and_get_task(app: Flask) -> None:
    with app.app_context():
        task_id = repository.create_task("Preparar portafolio", "Revisar proyecto")
        task = repository.get_task(task_id)

        assert task is not None
        assert task["title"] == "Preparar portafolio"
        assert task["description"] == "Revisar proyecto"
        assert task["is_completed"] == 0


def test_create_rejects_whitespace_only_title(app: Flask) -> None:
    with app.app_context():
        with pytest.raises(ValueError, match="title is required"):
            repository.create_task("   ")

        assert repository.list_tasks() == []


def test_list_tasks_places_pending_first(app: Flask) -> None:
    with app.app_context():
        completed_id = repository.create_task("Completada")
        pending_id = repository.create_task("Pendiente")
        repository.set_task_completed(completed_id, True)

        tasks = repository.list_tasks()

        assert [task["id"] for task in tasks] == [pending_id, completed_id]


def test_update_task(app: Flask) -> None:
    with app.app_context():
        task_id = repository.create_task("Título original")

        updated = repository.update_task(task_id, "Título nuevo", "Descripción nueva")
        task = repository.get_task(task_id)

        assert updated is True
        assert task is not None
        assert task["title"] == "Título nuevo"
        assert task["description"] == "Descripción nueva"


def test_set_task_completed(app: Flask) -> None:
    with app.app_context():
        task_id = repository.create_task("Alternar estado")

        assert repository.set_task_completed(task_id, True) is True
        assert repository.get_task(task_id)["is_completed"] == 1
        assert repository.set_task_completed(task_id, False) is True
        assert repository.get_task(task_id)["is_completed"] == 0


def test_delete_task(app: Flask) -> None:
    with app.app_context():
        task_id = repository.create_task("Eliminar")

        assert repository.delete_task(task_id) is True
        assert repository.get_task(task_id) is None


def test_missing_task_operations(app: Flask) -> None:
    with app.app_context():
        assert repository.get_task(999) is None
        assert repository.update_task(999, "No existe") is False
        assert repository.set_task_completed(999, True) is False
        assert repository.delete_task(999) is False
