import uuid
from typing import Any, cast

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _unique(base: str) -> str:
    """Generate a unique name to avoid conflicts across test runs."""
    return f"{base}_{uuid.uuid4().hex[:8]}"


def _create_person(name: str) -> dict[str, Any]:
    response = client.post("/api/persons", json={"name": name})
    assert response.status_code == 201
    return cast("dict[str, Any]", response.json())


def test_create_person() -> None:
    """Test creating a new person."""
    name = _unique("Alice")
    response = client.post("/api/persons", json={"name": name})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == name
    assert "id" in data


def test_create_person_duplicate_name() -> None:
    """Test that creating a person with a duplicate name fails."""
    unique_name = _unique("DuplicateTestPerson")
    client.post("/api/persons", json={"name": unique_name})
    response = client.post("/api/persons", json={"name": unique_name})
    assert response.status_code == 409


def test_create_person_empty_name() -> None:
    """Test that creating a person with empty name fails."""
    response = client.post("/api/persons", json={"name": ""})
    assert response.status_code == 422


def test_get_persons() -> None:
    """Test getting all persons."""
    _create_person(_unique("GetPersonsTest1"))
    _create_person(_unique("GetPersonsTest2"))

    response = client.get("/api/persons")
    assert response.status_code == 200
    data = cast("list[dict[str, Any]]", response.json())
    assert isinstance(data, list)
    assert len(data) >= 2


def test_update_person() -> None:
    """Test updating a person's name."""
    person = _create_person(_unique("UpdatePersonOriginal"))
    person_id = person["id"]
    new_name = _unique("UpdatePersonUpdated")

    response = client.put(f"/api/persons/{person_id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name
    assert data["id"] == person_id


def test_update_person_not_found() -> None:
    """Test updating a nonexistent person."""
    response = client.put("/api/persons/99999", json={"name": "Nobody"})
    assert response.status_code == 404


def test_update_person_duplicate_name() -> None:
    """Test updating a person with a name that already exists."""
    name_a = _unique("UpdateDupA")
    name_b = _unique("UpdateDupB")
    _create_person(name_a)
    person_b = _create_person(name_b)
    response = client.put(f"/api/persons/{person_b['id']}", json={"name": name_a})
    assert response.status_code == 409


def test_delete_person() -> None:
    """Test deleting a person with no assigned tasks."""
    person = _create_person(_unique("DeleteablePersonNoTasks"))
    response = client.delete(f"/api/persons/{person['id']}")
    assert response.status_code == 204


def test_delete_person_not_found() -> None:
    """Test deleting a nonexistent person."""
    response = client.delete("/api/persons/99999")
    assert response.status_code == 404


def test_delete_person_with_assigned_tasks() -> None:
    """Test that deleting a person assigned to tasks fails."""
    person = _create_person(_unique("PersonWithTasks"))
    client.post("/api/todos", json={"title": _unique("Task for deletion test"), "assigned_to_id": person["id"]})

    response = client.delete(f"/api/persons/{person['id']}")
    assert response.status_code == 409


def test_create_todo_with_assignment() -> None:
    """Test creating a todo with an assigned person."""
    person = _create_person(_unique("AssignedTodoCreator"))
    response = client.post("/api/todos", json={"title": _unique("Assigned Task"), "assigned_to_id": person["id"]})
    assert response.status_code == 201
    data = response.json()
    assert data["assigned_to_id"] == person["id"]
    assert data["assigned_to_name"] == person["name"]


def test_create_todo_without_assignment() -> None:
    """Test creating a todo without assignment."""
    response = client.post("/api/todos", json={"title": _unique("Unassigned Task")})
    assert response.status_code == 201
    data = response.json()
    assert data["assigned_to_id"] is None
    assert data["assigned_to_name"] is None


def test_assign_todo() -> None:
    """Test assigning a todo to a person."""
    person = _create_person(_unique("AssignTargetPerson"))
    todo_response = client.post("/api/todos", json={"title": _unique("Todo to assign")})
    todo_id = todo_response.json()["id"]

    response = client.patch(f"/api/todos/{todo_id}/assign", json={"assigned_to_id": person["id"]})
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_to_id"] == person["id"]
    assert data["assigned_to_name"] == person["name"]


def test_unassign_todo() -> None:
    """Test removing assignment from a todo."""
    person = _create_person(_unique("UnassignTargetPerson"))
    todo_response = client.post(
        "/api/todos", json={"title": _unique("Todo to unassign"), "assigned_to_id": person["id"]},
    )
    todo_id = todo_response.json()["id"]

    response = client.patch(f"/api/todos/{todo_id}/assign", json={"assigned_to_id": None})
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_to_id"] is None
    assert data["assigned_to_name"] is None


def test_filter_todos_by_person() -> None:
    """Test filtering todos by assigned person."""
    person = _create_person(_unique("FilterTestPerson"))
    client.post("/api/todos", json={"title": _unique("Filtered Todo"), "assigned_to_id": person["id"]})
    client.post("/api/todos", json={"title": _unique("Unfiltered Todo")})

    response = client.get(f"/api/todos?assigned_to={person['id']}")
    assert response.status_code == 200
    data = cast("list[dict[str, Any]]", response.json())
    assert len(data) >= 1
    assert all(t["assigned_to_id"] == person["id"] for t in data)


def test_filter_todos_unassigned() -> None:
    """Test filtering todos with no assignment."""
    person = _create_person(_unique("FilterUnassignedPerson"))
    client.post("/api/todos", json={"title": _unique("FilterUnassigned Todo")})
    client.post("/api/todos", json={"title": _unique("FilterAssigned Todo"), "assigned_to_id": person["id"]})

    response = client.get("/api/todos?assigned_to=null")
    assert response.status_code == 200
    data = cast("list[dict[str, Any]]", response.json())
    assert all(t["assigned_to_id"] is None for t in data)
