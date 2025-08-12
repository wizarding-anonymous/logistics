import pytest
from fastapi.testclient import TestClient
import os

from search.main import app

@pytest.fixture(scope="module")
def client() -> TestClient:
    """Fixture to create a TestClient."""
    with TestClient(app) as c:
        yield c
