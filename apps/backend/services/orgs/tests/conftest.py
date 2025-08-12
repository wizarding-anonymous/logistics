import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import uuid
from jose import jwt
from datetime import datetime, timedelta

from orgs.main import app
from orgs.database import Base, get_db
from orgs.models import Organization, user_organization_link
import orgs.schemas as schemas

# --- Test Database Setup ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://admin:password@postgres/marketplace_test")

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[async_sessionmaker, None]:
    """Fixture to create and teardown the test database schema."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield TestingSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(test_db: async_sessionmaker) -> TestClient:
    """Fixture to create a TestClient with an overridden DB dependency."""

    async def override_get_db() -> AsyncGenerator:
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

# --- Authentication Fixtures ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_long_and_random")
ALGORITHM = "HS256"

def create_test_token(user_id: uuid.UUID, roles: list[str] = None) -> str:
    """Utility to create a JWT for a test user."""
    if roles is None:
        roles = []

    claims = {
        "sub": str(user_id),
        "roles": roles,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)

@pytest.fixture(scope="function")
def auth_token_factory():
    """Fixture to provide the token creation utility to tests."""
    return create_test_token

# --- Data Fixtures ---
@pytest.fixture(scope="function")
async def test_user_owner(test_db: async_sessionmaker) -> dict:
    """Fixture to create a test user."""
    return {"id": uuid.uuid4()}


@pytest.fixture(scope="function")
async def test_organization(test_db: async_sessionmaker, test_user_owner: dict) -> Organization:
    """Fixture to create a test organization with an owner."""
    async with test_db() as session:
        org = Organization(name="Test Corp", description="A test organization")
        session.add(org)
        await session.commit()
        await session.refresh(org)

        # Link the owner to the organization
        stmt = user_organization_link.insert().values(
            user_id=test_user_owner["id"],
            organization_id=org.id,
            role="owner"
        )
        await session.execute(stmt)
        await session.commit()
        return org
