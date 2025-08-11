import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import uuid
from unittest.mock import patch

from docs.main import app
from docs.database import Base, get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def mock_s3_client():
    with patch('docs.s3_client.s3_client') as mock_client:
        mock_client.generate_presigned_url.return_value = "http://mock-s3-url.com/upload"
        yield mock_client

@pytest.fixture(scope="function")
def client(mock_s3_client) -> TestClient:
    # Since this service might interact with a DB, we set up a test DB
    # even if the tested endpoints don't use it directly.
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://admin:password@localhost/marketplace_test")
    engine = create_async_engine(TEST_DATABASE_URL)
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

    async def override_get_db() -> AsyncGenerator:
        async with TestingSessionLocal() as session:
            # We don't need to create tables if the models are not used in these tests
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
