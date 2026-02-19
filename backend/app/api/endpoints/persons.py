from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Person, TodoItem

DbDependency = Annotated[Session, Depends(get_db)]

router = APIRouter()


class PersonCreate(BaseModel):
    """Request model for creating a person."""

    name: str = Field(..., min_length=1, max_length=200)


class PersonUpdate(BaseModel):
    """Request model for updating a person."""

    name: str = Field(..., min_length=1, max_length=200)


class PersonResponse(BaseModel):
    """Response model for a person."""

    id: int
    name: str

    model_config = {"from_attributes": True}


@router.get("/persons")
def get_persons(db: DbDependency) -> list[PersonResponse]:
    """Get all persons."""
    stmt = select(Person).order_by(Person.name)
    persons = db.execute(stmt).scalars().all()
    return [PersonResponse(id=p.id, name=p.name) for p in persons]


@router.post("/persons", status_code=HTTPStatus.CREATED)
def create_person(person: PersonCreate, db: DbDependency) -> PersonResponse:
    """Create a new person."""
    existing = db.execute(select(Person).where(Person.name == person.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="A person with this name already exists")

    db_person = Person(name=person.name)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return PersonResponse(id=db_person.id, name=db_person.name)


@router.put("/persons/{person_id}")
def update_person(person_id: int, person: PersonUpdate, db: DbDependency) -> PersonResponse:
    """Update a person's name."""
    stmt = select(Person).where(Person.id == person_id)
    db_person = db.execute(stmt).scalar_one_or_none()

    if not db_person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    existing = db.execute(
        select(Person).where(Person.name == person.name, Person.id != person_id),
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="A person with this name already exists")

    db_person.name = person.name
    db.commit()
    db.refresh(db_person)
    return PersonResponse(id=db_person.id, name=db_person.name)


@router.delete("/persons/{person_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_person(person_id: int, db: DbDependency) -> None:
    """Delete a person. Fails if the person is assigned to any tasks."""
    stmt = select(Person).where(Person.id == person_id)
    db_person = db.execute(stmt).scalar_one_or_none()

    if not db_person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    assigned_count = db.execute(
        select(TodoItem).where(TodoItem.assigned_to_id == person_id),
    ).scalars().first()
    if assigned_count is not None:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Cannot delete a person who is currently assigned to tasks",
        )

    db.delete(db_person)
    db.commit()
