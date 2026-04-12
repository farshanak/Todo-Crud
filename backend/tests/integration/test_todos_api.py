"""
Integration tests for the Todos HTTP API.

These tests exercise the real FastAPI app via TestClient. They validate
wiring end-to-end: route registration, Pydantic (de)serialization, status
codes, and in-memory store behavior.

The `client` and `reset_store` fixtures come from backend/tests/conftest.py.
"""
from fastapi.testclient import TestClient


def test_list_empty(client: TestClient) -> None:
    res = client.get("/todos")
    assert res.status_code == 200
    assert res.json() == []


def test_create_todo_returns_id_and_defaults_done_false(client: TestClient) -> None:
    res = client.post("/todos", json={"title": "buy milk"})
    assert res.status_code == 201
    body = res.json()
    assert body["id"] == 1
    assert body["title"] == "buy milk"
    assert body["done"] is False


def test_create_multiple_ids_increment(client: TestClient) -> None:
    first = client.post("/todos", json={"title": "a"}).json()
    second = client.post("/todos", json={"title": "b"}).json()
    assert first["id"] == 1
    assert second["id"] == 2


def test_list_returns_created_todos(client: TestClient) -> None:
    client.post("/todos", json={"title": "one"})
    client.post("/todos", json={"title": "two", "done": True})
    res = client.get("/todos")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    titles = {t["title"] for t in data}
    assert titles == {"one", "two"}


def test_update_changes_title_and_done(client: TestClient) -> None:
    created = client.post("/todos", json={"title": "draft"}).json()
    res = client.put(
        f"/todos/{created['id']}",
        json={"title": "final", "done": True},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == created["id"]
    assert body["title"] == "final"
    assert body["done"] is True


def test_update_missing_returns_404(client: TestClient) -> None:
    res = client.put("/todos/999", json={"title": "nope", "done": False})
    assert res.status_code == 404
    assert res.json()["detail"] == "Todo not found"


def test_delete_removes_todo(client: TestClient) -> None:
    created = client.post("/todos", json={"title": "temp"}).json()
    res = client.delete(f"/todos/{created['id']}")
    assert res.status_code == 204
    listing = client.get("/todos").json()
    assert listing == []


def test_delete_missing_returns_404(client: TestClient) -> None:
    res = client.delete("/todos/999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Todo not found"


def test_create_with_due_at_round_trips_on_get(client: TestClient) -> None:
    due = "2026-05-01T09:30:00"
    created = client.post(
        "/todos", json={"title": "ship", "due_at": due, "priority": "high"}
    ).json()
    listed = client.get("/todos").json()
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]
    assert listed[0]["due_at"].startswith("2026-05-01T09:30:00")
    assert listed[0]["priority"] == "high"


def test_create_without_priority_defaults_to_medium(client: TestClient) -> None:
    body = client.post("/todos", json={"title": "no prio"}).json()
    assert body["priority"] == "medium"
    assert body["due_at"] is None


def test_create_with_invalid_priority_returns_422(client: TestClient) -> None:
    res = client.post("/todos", json={"title": "bad", "priority": "critical"})
    assert res.status_code == 422


def test_update_changes_due_at_and_priority(client: TestClient) -> None:
    created = client.post("/todos", json={"title": "t"}).json()
    res = client.put(
        f"/todos/{created['id']}",
        json={
            "title": "t",
            "done": False,
            "due_at": "2026-06-15T12:00:00",
            "priority": "urgent",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["due_at"].startswith("2026-06-15T12:00:00")
    assert body["priority"] == "urgent"
