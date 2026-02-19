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
    assigned_to_name: str | None

    model_config = {"from_attributes": True}


def _todo_response(todo: TodoItem) -> TodoItemResponse:
    return TodoItemResponse(
        id=todo.id,
        title=todo.title,
        is_done=todo.is_done,
        created_at=todo.created_at.isoformat(),
        assigned_to_id=todo.assigned_to_id,
        assigned_to_name=todo.assigned_to.name if todo.assigned_to else None,
    )


@router.get("/todos")
def get_todos(
    db: DbDependency,
    assigned_to: Annotated[str | None, Query()] = None,
) -> list[TodoItemResponse]:
    """Get all todo items, optionally filtered by assignment.

    - assigned_to=null: returns todos with no assignment
    - assigned_to=<id>: returns todos assigned to that person
    - (omitted): returns all todos
    """
    stmt = select(TodoItem).order_by(TodoItem.created_at.desc())
    if assigned_to is not None:
        if assigned_to.lower() == "null":
            stmt = stmt.where(TodoItem.assigned_to_id.is_(None))
        else:
            try:
                person_id = int(assigned_to)
            except ValueError as err:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="assigned_to must be 'null' or an integer",
                ) from err
            stmt = stmt.where(TodoItem.assigned_to_id == person_id)
    todos = db.execute(stmt).scalars().all()
    return [_todo_response(todo) for todo in todos]


@router.post("/todos", status_code=HTTPStatus.CREATED)
def create_todo(
    todo: TodoItemCreate,
    db: DbDependency,
    response: Response,
) -> TodoItemResponse:
    """Create a new todo item."""
    if todo.assigned_to_id is not None:
        person = db.execute(select(Person).where(Person.id == todo.assigned_to_id)).scalar_one_or_none()
        if not person:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    db_todo = TodoItem(title=todo.title, is_done=False, assigned_to_id=todo.assigned_to_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    response.headers["Location"] = f"/api/todos/{db_todo.id}"
    return _todo_response(db_todo)


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
    return _todo_response(todo)


@router.patch("/todos/{todo_id}/assign")
def assign_todo(todo_id: int, body: TodoItemUpdate, db: DbDependency) -> TodoItemResponse:
    """Assign or unassign a todo item. Pass assigned_to_id=null to unassign."""
    stmt = select(TodoItem).where(TodoItem.id == todo_id)
    todo = db.execute(stmt).scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo item not found")

    if body.assigned_to_id is not None:
        person = db.execute(select(Person).where(Person.id == body.assigned_to_id)).scalar_one_or_none()
        if not person:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    todo.assigned_to_id = body.assigned_to_id
    db.commit()
    db.refresh(todo)
    return _todo_response(todo)


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: DbDependency) -> None:
    """Delete a todo item."""
    stmt = select(TodoItem).where(TodoItem.id == todo_id)
    todo = db.execute(stmt).scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo item not found")

    db.delete(todo)
    db.commit()
