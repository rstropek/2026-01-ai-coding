from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Person, TodoItem

DbDependency = Annotated[Session, Depends(get_db)]

router = APIRouter()


class PersonCreate(BaseModel):
    """Request model for creating a person."""

    name: str = Field(..., min_length=1, max_length=100)


class PersonUpdate(BaseModel):
    """Request model for updating a person."""

    name: str = Field(..., min_length=1, max_length=100)


class PersonResponse(BaseModel):
    """Response model for a person."""

    id: int
    name: str

    model_config = {"from_attributes": True}


@router.get("/people")
def get_people(db: DbDependency) -> list[PersonResponse]:
    """Get all people."""
    stmt = select(Person).order_by(Person.name)
    people = db.execute(stmt).scalars().all()
    return [PersonResponse(id=person.id, name=person.name) for person in people]


@router.post("/people", status_code=HTTPStatus.CREATED)
def create_person(
    person: PersonCreate,
    db: DbDependency,
    response: Response,
) -> PersonResponse:
    """Create a new person."""
    # Check if person with this name already exists
    stmt = select(Person).where(Person.name == person.name)
    existing = db.execute(stmt).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A person with this name already exists",
        )

    db_person = Person(name=person.name)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    response.headers["Location"] = f"/api/people/{db_person.id}"
    return PersonResponse(id=db_person.id, name=db_person.name)


@router.patch("/people/{person_id}")
def update_person(
    person_id: int,
    person: PersonUpdate,
    db: DbDependency,
) -> PersonResponse:
    """Update a person's name."""
    stmt = select(Person).where(Person.id == person_id)
    db_person = db.execute(stmt).scalar_one_or_none()

    if not db_person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    # Check if another person with this name already exists
    stmt = select(Person).where(Person.name == person.name, Person.id != person_id)
    existing = db.execute(stmt).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A person with this name already exists",
        )

    db_person.name = person.name
    db.commit()
    db.refresh(db_person)
    return PersonResponse(id=db_person.id, name=db_person.name)


@router.delete("/people/{person_id}", status_code=204)
def delete_person(person_id: int, db: DbDependency) -> None:
    """Delete a person."""
    stmt = select(Person).where(Person.id == person_id)
    db_person = db.execute(stmt).scalar_one_or_none()

    if not db_person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    # Check if person is assigned to any todos
    todo_stmt = select(TodoItem).where(TodoItem.assigned_to_id == person_id).limit(1)
    assigned_todo = db.execute(todo_stmt).scalar_one_or_none()

    if assigned_todo:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Cannot delete person who is assigned to tasks",
        )

    db.delete(db_person)
    db.commit()
