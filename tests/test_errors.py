from flask import Flask
from flask.testing import FlaskClient


def test_404_uses_custom_page(client: FlaskClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert b"P\xc3\xa1gina no encontrada" in response.data


def test_500_uses_custom_page(app: Flask, client: FlaskClient) -> None:
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/_test/internal-error")
    def internal_error_for_test() -> None:
        raise RuntimeError("isolated test error")

    response = client.get("/_test/internal-error")

    assert response.status_code == 500
    assert b"Algo sali\xc3\xb3 mal" in response.data
