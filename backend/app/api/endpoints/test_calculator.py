from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_add_two_integers() -> None:
    response = client.post("/api/calculator/add", json={"a": 3, "b": 4})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"result": 7.0}


def test_add_two_floats() -> None:
    response = client.post("/api/calculator/add", json={"a": 1.5, "b": 2.5})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"result": 4.0}


def test_add_negative_numbers() -> None:
    response = client.post("/api/calculator/add", json={"a": -3, "b": 5})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"result": 2.0}
