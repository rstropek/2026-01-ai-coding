from typing import Any, cast

from fastapi.testclient import TestClient

from app.main import app

# Use the same database as the app (configured via settings)
client = TestClient(app)


def test_create_todo() -> None:
    """Test creating a new todo item."""
    response = client.post("/api/todos", json={"title": "Test Todo"})
    assert response.status_code == 201  # noqa: PLR2004
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["is_done"] is False
    assert "id" in data
    assert "created_at" in data
    assert "location" in response.headers
    assert response.headers["location"] == f"/api/todos/{data['id']}"


def test_get_todos() -> None:
    """Test getting all todo items."""
    # Create some todos
    client.post("/api/todos", json={"title": "Todo 1"})
    client.post("/api/todos", json={"title": "Todo 2"})

    # Get all todos
    response = client.get("/api/todos")
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert isinstance(data, list)
    todos = cast("list[dict[str, Any]]", data)
    assert len(todos) >= 2  # noqa: PLR2004


def test_mark_todo_done() -> None:
    """Test marking a todo as done."""
    # Create a todo
    create_response = client.post("/api/todos", json={"title": "Todo to complete"})
    todo_id = create_response.json()["id"]

    # Mark it as done
    response = client.patch(f"/api/todos/{todo_id}/done")
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert data["is_done"] is True
    assert data["id"] == todo_id


def test_mark_nonexistent_todo_done() -> None:
    """Test marking a nonexistent todo as done."""
    response = client.patch("/api/todos/99999/done")
    assert response.status_code == 404  # noqa: PLR2004


def test_delete_todo() -> None:
    """Test deleting a todo item."""
    # Create a todo
    create_response = client.post("/api/todos", json={"title": "Todo to delete"})
    todo_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204  # noqa: PLR2004

    # Verify it's gone by trying to mark it done
    response = client.patch(f"/api/todos/{todo_id}/done")
    assert response.status_code == 404  # noqa: PLR2004


def test_delete_nonexistent_todo() -> None:
    """Test deleting a nonexistent todo."""
    response = client.delete("/api/todos/99999")
    assert response.status_code == 404  # noqa: PLR2004


def test_create_todo_empty_title() -> None:
    """Test creating a todo with empty title."""
    response = client.post("/api/todos", json={"title": ""})
    assert response.status_code == 422  # noqa: PLR2004
