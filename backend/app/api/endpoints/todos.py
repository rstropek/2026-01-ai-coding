from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Person, TodoItem

DbDependency = Annotated[Session, Depends(get_db)]

router = APIRouter()


class TodoItemCreate(BaseModel):
    """Request model for creating a todo item."""

    title: str = Field(..., min_length=1, max_length=200)
    assigned_to_id: int | None = None


class TodoItemUpdate(BaseModel):
    """Request model for updating a todo item's assignment."""

    assigned_to_id: int | None = None


class TodoItemResponse(BaseModel):
    """Response model for a todo item."""

    id: int
    title: str
    is_done: bool
    created_at: str
    assigned_to_id: int | None

    model_config = {"from_attributes": True}


@router.get("/todos")
def get_todos(
    db: DbDependency,
    assigned_to_id: Annotated[int | None, Query(description="Filter by assigned person ID")] = None,
) -> list[TodoItemResponse]:
    """Get all todo items, optionally filtered by assignment."""
    stmt = select(TodoItem)

    # Apply filter if assigned_to_id is provided
    if assigned_to_id is not None:
        stmt = stmt.where(TodoItem.assigned_to_id == assigned_to_id)

    stmt = stmt.order_by(TodoItem.created_at.desc())
    todos = db.execute(stmt).scalars().all()
    return [
        TodoItemResponse(
            id=todo.id,
            title=todo.title,
            is_done=todo.is_done,
            created_at=todo.created_at.isoformat(),
            assigned_to_id=todo.assigned_to_id,
        )
        for todo in todos
    ]


@router.post("/todos", status_code=HTTPStatus.CREATED)
def create_todo(
    todo: TodoItemCreate,
    db: DbDependency,
    response: Response,
) -> TodoItemResponse:
    """Create a new todo item."""
    # Validate that the person exists if assigned_to_id is provided
    if todo.assigned_to_id is not None:
        stmt = select(Person).where(Person.id == todo.assigned_to_id)
        person = db.execute(stmt).scalar_one_or_none()
        if not person:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    db_todo = TodoItem(title=todo.title, is_done=False, assigned_to_id=todo.assigned_to_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    response.headers["Location"] = f"/api/todos/{db_todo.id}"
    return TodoItemResponse(
        id=db_todo.id,
        title=db_todo.title,
        is_done=db_todo.is_done,
        created_at=db_todo.created_at.isoformat(),
        assigned_to_id=db_todo.assigned_to_id,
    )


@router.patch("/todos/{todo_id}/done")
def mark_todo_done(todo_id: int, db: DbDependency) -> TodoItemResponse:
    """Mark a todo item as done."""
    stmt = select(TodoItem).where(TodoItem.id == todo_id)
    todo = db.execute(stmt).scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo item not found")

    todo.is_done = True
    db.commit()
    db.refresh(todo)
    return TodoItemResponse(
        id=todo.id,
        title=todo.title,
        is_done=todo.is_done,
        created_at=todo.created_at.isoformat(),
        assigned_to_id=todo.assigned_to_id,
    )


@router.patch("/todos/{todo_id}/assign")
def assign_todo(
    todo_id: int,
    update: TodoItemUpdate,
    db: DbDependency,
) -> TodoItemResponse:
    """Assign or unassign a todo item to/from a person."""
    stmt = select(TodoItem).where(TodoItem.id == todo_id)
    todo = db.execute(stmt).scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo item not found")

    # Validate that the person exists if assigned_to_id is provided
    if update.assigned_to_id is not None:
        person_stmt = select(Person).where(Person.id == update.assigned_to_id)
        person = db.execute(person_stmt).scalar_one_or_none()
        if not person:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    todo.assigned_to_id = update.assigned_to_id
    db.commit()
    db.refresh(todo)
    return TodoItemResponse(
        id=todo.id,
        title=todo.title,
        is_done=todo.is_done,
        created_at=todo.created_at.isoformat(),
        assigned_to_id=todo.assigned_to_id,
    )


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: DbDependency) -> None:
    """Delete a todo item."""
    stmt = select(TodoItem).where(TodoItem.id == todo_id)
    todo = db.execute(stmt).scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo item not found")

    db.delete(todo)
    db.commit()
