from time import time

from fastapi.testclient import TestClient

from app.main import app

# Use the same database as the app (configured via settings)
client = TestClient(app)


def _unique_name(base: str) -> str:
    """Generate a unique name using timestamp."""
    return f"{base}_{int(time() * 1000000)}"


def test_create_person() -> None:
    """Test creating a new person."""
    unique_name = _unique_name("John_Doe")
    response = client.post("/api/people", json={"name": unique_name})
    assert response.status_code == 201  # noqa: PLR2004
    data = response.json()
    assert data["name"] == unique_name
    assert "id" in data
    assert "location" in response.headers
    assert response.headers["location"] == f"/api/people/{data['id']}"


def test_get_people() -> None:
    """Test getting all people."""
    # Create some people
    client.post("/api/people", json={"name": "Person 1"})
    client.post("/api/people", json={"name": "Person 2"})

    # Get all people
    response = client.get("/api/people")
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # noqa: PLR2004


def test_create_person_duplicate_name() -> None:
    """Test creating a person with a duplicate name."""
    # Create first person
    unique_name = _unique_name("Duplicate_Name")
    client.post("/api/people", json={"name": unique_name})

    # Try to create another with same name
    response = client.post("/api/people", json={"name": unique_name})
    assert response.status_code == 409  # noqa: PLR2004


def test_create_person_empty_name() -> None:
    """Test creating a person with empty name."""
    response = client.post("/api/people", json={"name": ""})
    assert response.status_code == 422  # noqa: PLR2004


def test_update_person() -> None:
    """Test updating a person's name."""
    # Create a person
    old_name = _unique_name("Old_Name")
    new_name = _unique_name("New_Name")
    create_response = client.post("/api/people", json={"name": old_name})
    person_id = create_response.json()["id"]

    # Update the name
    response = client.patch(f"/api/people/{person_id}", json={"name": new_name})
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert data["name"] == new_name
    assert data["id"] == person_id


def test_update_person_duplicate_name() -> None:
    """Test updating a person to a duplicate name."""
    # Create two people
    first_name = _unique_name("First_Person")
    second_name = _unique_name("Second_Person")
    client.post("/api/people", json={"name": first_name})
    create_response = client.post("/api/people", json={"name": second_name})
    person_id = create_response.json()["id"]

    # Try to update second person to first person's name
    response = client.patch(f"/api/people/{person_id}", json={"name": first_name})
    assert response.status_code == 409  # noqa: PLR2004


def test_update_nonexistent_person() -> None:
    """Test updating a nonexistent person."""
    response = client.patch("/api/people/99999", json={"name": "New Name"})
    assert response.status_code == 404  # noqa: PLR2004


def test_delete_person() -> None:
    """Test deleting a person."""
    # Create a person
    unique_name = _unique_name("To_Delete")
    create_response = client.post("/api/people", json={"name": unique_name})
    person_id = create_response.json()["id"]

    # Delete the person
    response = client.delete(f"/api/people/{person_id}")
    assert response.status_code == 204  # noqa: PLR2004

    # Verify it's gone
    response = client.patch(f"/api/people/{person_id}", json={"name": "Updated"})
    assert response.status_code == 404  # noqa: PLR2004


def test_delete_nonexistent_person() -> None:
    """Test deleting a nonexistent person."""
    response = client.delete("/api/people/99999")
    assert response.status_code == 404  # noqa: PLR2004


def test_delete_person_assigned_to_tasks() -> None:
    """Test deleting a person who is assigned to tasks."""
    # Create a person and assign them to a todo
    unique_name = _unique_name("Busy_Person")
    person_response = client.post("/api/people", json={"name": unique_name})
    person_id = person_response.json()["id"]
    client.post("/api/todos", json={"title": "Assigned Task", "assigned_to_id": person_id})

    # Try to delete the person
    response = client.delete(f"/api/people/{person_id}")
    assert response.status_code == 409  # noqa: PLR2004
