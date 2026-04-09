from itertools import count

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Ensure each test starts with an empty store and fresh ID sequence."""
    main._todos.clear()
    main._ids = count(1)
    yield
    main._todos.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(main.app)


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
