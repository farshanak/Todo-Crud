from itertools import count

from config import settings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


class Todo(TodoIn):
    id: int


_ids = count(1)
_todos: dict[int, Todo] = {}


@app.get("/todos", response_model=list[Todo])
def list_todos() -> list[Todo]:
    return list(_todos.values())


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
