from collections.abc import Callable

import pytest
from flask import Flask
from flask.testing import FlaskClient

from task_manager.tasks import repository


def test_index_lists_tasks(app: Flask, client: FlaskClient) -> None:
    with app.app_context():
        repository.create_task("Tarea visible", "Descripción visible")

    response = client.get("/")

    assert response.status_code == 200
    assert b"Tarea visible" in response.data
    assert b"Descripci\xc3\xb3n visible" in response.data


def test_create_task(
    app: Flask, client: FlaskClient, csrf_token: Callable[[], str]
) -> None:
    response = client.post(
        "/tasks/create",
        data={
            "title": "Nueva tarea",
            "description": "Detalle",
            "csrf_token": csrf_token(),
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    with app.app_context():
        tasks = repository.list_tasks()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Nueva tarea"


def test_create_requires_title(
    app: Flask, client: FlaskClient, csrf_token: Callable[[], str]
) -> None:
    response = client.post(
        "/tasks/create",
        data={
            "title": "   ",
            "description": "Detalle",
            "csrf_token": csrf_token(),
        },
    )

    assert response.status_code == 400
    assert b"El t\xc3\xadtulo es obligatorio." in response.data
    with app.app_context():
        assert repository.list_tasks() == []


def test_edit_task(
    app: Flask, client: FlaskClient, csrf_token: Callable[[], str]
) -> None:
    with app.app_context():
        task_id = repository.create_task("Original")

    get_response = client.get(f"/tasks/{task_id}/edit")
    post_response = client.post(
        f"/tasks/{task_id}/edit",
        data={
            "title": "Editada",
            "description": "Actualizada",
            "csrf_token": csrf_token(),
        },
    )

    assert get_response.status_code == 200
    assert b"Original" in get_response.data
    assert post_response.status_code == 302
    with app.app_context():
        task = repository.get_task(task_id)
        assert task["title"] == "Editada"


def test_edit_requires_title(
    app: Flask, client: FlaskClient, csrf_token: Callable[[], str]
) -> None:
    with app.app_context():
        task_id = repository.create_task("Original")

    response = client.post(
        f"/tasks/{task_id}/edit",
        data={"title": "", "csrf_token": csrf_token()},
    )

    assert response.status_code == 400
    assert b"El t\xc3\xadtulo es obligatorio." in response.data


def test_toggle_task(
    app: Flask, client: FlaskClient, csrf_token: Callable[[], str]
) -> None:
    with app.app_context():
        task_id = repository.create_task("Alternar")

    token = csrf_token()
    response = client.post(f"/tasks/{task_id}/toggle", data={"csrf_token": token})
    assert response.status_code == 302
    with app.app_context():
        assert repository.get_task(task_id)["is_completed"] == 1

    response = client.post(f"/tasks/{task_id}/toggle", data={"csrf_token": token})
    assert response.status_code == 302
    with app.app_context():
        assert repository.get_task(task_id)["is_completed"] == 0


def test_delete_task(
    app: Flask, client: FlaskClient, csrf_token: Callable[[], str]
) -> None:
    with app.app_context():
        task_id = repository.create_task("Eliminar")

    response = client.post(
        f"/tasks/{task_id}/delete", data={"csrf_token": csrf_token()}
    )

    assert response.status_code == 302
    with app.app_context():
        assert repository.get_task(task_id) is None


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/tasks/999/edit"),
        ("post", "/tasks/999/edit"),
        ("post", "/tasks/999/toggle"),
        ("post", "/tasks/999/delete"),
    ],
)
def test_missing_task_returns_404(
    client: FlaskClient,
    csrf_token: Callable[[], str],
    method: str,
    path: str,
) -> None:
    data = (
        {"title": "No existe", "csrf_token": csrf_token()} if method == "post" else None
    )
    response = getattr(client, method)(path, data=data)

    assert response.status_code == 404


@pytest.mark.parametrize("csrf_value", [None, "invalid-token"])
def test_create_rejects_missing_or_invalid_csrf(
    app: Flask,
    client: FlaskClient,
    csrf_token: Callable[[], str],
    csrf_value: str | None,
) -> None:
    csrf_token()
    data = {"title": "No debe persistirse"}
    if csrf_value is not None:
        data["csrf_token"] = csrf_value

    response = client.post("/tasks/create", data=data)

    assert response.status_code == 400
    with app.app_context():
        assert repository.list_tasks() == []
