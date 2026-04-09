"""
Shared test fixtures for the Todo backend.

Rules:
- This is the single source of truth for shared pytest fixtures.
- Fixtures that reset module-level state live here so every test starts clean.
"""
from itertools import count

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Each test starts with an empty in-memory store and fresh id sequence."""
    main._todos.clear()
    main._ids = count(1)
    yield
    main._todos.clear()


@pytest.fixture
def client() -> TestClient:
    """A fresh FastAPI TestClient against the real app (integration)."""
    return TestClient(main.app)
