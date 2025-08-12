import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import uuid
from jose import jwt
from datetime import datetime, timedelta

from catalog.main import app
from catalog.database import Base, get_db
from catalog.models import ServiceOffering

# --- Test Database Setup ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://admin:password@localhost/marketplace_test")

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[async_sessionmaker, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield TestingSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(test_db: async_sessionmaker) -> TestClient:
    async def override_get_db() -> AsyncGenerator:
        async with test_db() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

# --- Authentication Fixtures ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_long_and_random")
ALGORITHM = "HS256"

def create_test_token(user_id: uuid.UUID, org_id: uuid.UUID, roles: list[str]) -> str:
    claims = {
        "sub": str(user_id),
        "org_id": str(org_id),
        "roles": roles,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)

@pytest.fixture(scope="function")
def auth_token_factory():
    return create_test_token

# --- Data Fixtures ---
@pytest.fixture(scope="function")
def test_supplier_user() -> dict:
    return {"id": uuid.uuid4(), "org_id": uuid.uuid4()}
