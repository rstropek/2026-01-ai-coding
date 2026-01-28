from time import time

from fastapi.testclient import TestClient

from app.main import app

# Use the same database as the app (configured via settings)
client = TestClient(app)


def _unique_name(base: str) -> str:
    """Generate a unique name using timestamp."""
    return f"{base}_{int(time() * 1000000)}"


def test_create_todo() -> None:
    """Test creating a new todo item."""
    response = client.post("/api/todos", json={"title": "Test Todo"})
    assert response.status_code == 201  # noqa: PLR2004
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["is_done"] is False
    assert data["assigned_to_id"] is None
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
    assert len(data) >= 2  # noqa: PLR2004


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


def test_create_todo_with_assignment() -> None:
    """Test creating a todo item assigned to a person."""
    # Create a person first
    unique_name = _unique_name("Alice")
    person_response = client.post("/api/people", json={"name": unique_name})
    person_id = person_response.json()["id"]

    # Create todo assigned to that person
    response = client.post("/api/todos", json={"title": "Assigned Todo", "assigned_to_id": person_id})
    assert response.status_code == 201  # noqa: PLR2004
    data = response.json()
    assert data["title"] == "Assigned Todo"
    assert data["assigned_to_id"] == person_id


def test_create_todo_with_nonexistent_person() -> None:
    """Test creating a todo assigned to a nonexistent person."""
    response = client.post("/api/todos", json={"title": "Test Todo", "assigned_to_id": 99999})
    assert response.status_code == 404  # noqa: PLR2004


def test_assign_todo() -> None:
    """Test assigning a todo to a person."""
    # Create a person and a todo
    unique_name = _unique_name("Bob")
    person_response = client.post("/api/people", json={"name": unique_name})
    person_id = person_response.json()["id"]
    todo_response = client.post("/api/todos", json={"title": "Unassigned Todo"})
    todo_id = todo_response.json()["id"]

    # Assign the todo
    response = client.patch(f"/api/todos/{todo_id}/assign", json={"assigned_to_id": person_id})
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert data["assigned_to_id"] == person_id


def test_unassign_todo() -> None:
    """Test unassigning a todo from a person."""
    # Create a person and an assigned todo
    unique_name = _unique_name("Charlie")
    person_response = client.post("/api/people", json={"name": unique_name})
    person_id = person_response.json()["id"]
    todo_response = client.post("/api/todos", json={"title": "Assigned", "assigned_to_id": person_id})
    todo_id = todo_response.json()["id"]

    # Unassign the todo
    response = client.patch(f"/api/todos/{todo_id}/assign", json={"assigned_to_id": None})
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert data["assigned_to_id"] is None


def test_assign_todo_to_nonexistent_person() -> None:
    """Test assigning a todo to a nonexistent person."""
    todo_response = client.post("/api/todos", json={"title": "Test Todo"})
    todo_id = todo_response.json()["id"]

    response = client.patch(f"/api/todos/{todo_id}/assign", json={"assigned_to_id": 99999})
    assert response.status_code == 404  # noqa: PLR2004


def test_filter_todos_by_person() -> None:
    """Test filtering todos by assigned person."""
    # Create two people
    person1_response = client.post("/api/people", json={"name": _unique_name("David")})
    person1_id = person1_response.json()["id"]
    person2_response = client.post("/api/people", json={"name": _unique_name("Eve")})
    person2_id = person2_response.json()["id"]

    # Create todos assigned to different people
    client.post("/api/todos", json={"title": "David's task", "assigned_to_id": person1_id})
    client.post("/api/todos", json={"title": "Eve's task", "assigned_to_id": person2_id})
    client.post("/api/todos", json={"title": "Unassigned task"})

    # Filter by person 1
    response = client.get(f"/api/todos?assigned_to_id={person1_id}")
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert all(todo["assigned_to_id"] == person1_id for todo in data)

    # Filter by unassigned (0)
    response = client.get("/api/todos?assigned_to_id=0")
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert all(todo["assigned_to_id"] is None for todo in data)

