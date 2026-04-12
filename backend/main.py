from datetime import datetime
from itertools import count
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings

Priority = Literal["low", "medium", "high", "urgent"]

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TodoIn(BaseModel):
    title: str
    done: bool = False
    due_at: datetime | None = None
    priority: Priority = "medium"


class Todo(TodoIn):
    id: int


_ids = count(1)
_todos: dict[int, Todo] = {}


@app.get("/todos", response_model=list[Todo])
def list_todos(
    q: str | None = Query(default=None),
    priority: Priority | None = Query(default=None),
    overdue: bool | None = Query(default=None),
) -> list[Todo]:
    items = list(_todos.values())
    if q:
        needle = q.lower()
        items = [t for t in items if needle in t.title.lower()]
    if priority is not None:
        items = [t for t in items if t.priority == priority]
    if overdue:
        now = datetime.utcnow()
        items = [
            t
            for t in items
            if t.due_at is not None
            and (t.due_at.replace(tzinfo=None) if t.due_at.tzinfo else t.due_at) < now
        ]
    return items


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoIn) -> Todo:
    todo = Todo(id=next(_ids), **payload.model_dump())
    _todos[todo.id] = todo
    return todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoIn) -> Todo:
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated = Todo(id=todo_id, **payload.model_dump())
    _todos[todo_id] = updated
    return updated


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del _todos[todo_id]
