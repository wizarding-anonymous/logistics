import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import uuid
from jose import jwt
from datetime import datetime, timedelta

from unittest.mock import patch

# This patch must be applied BEFORE the app and its dependencies are imported
# It replaces the KafkaProducer and KafkaConsumer classes with mocks
kafka_producer_patch = patch('kafka.KafkaProducer', autospec=True)
kafka_consumer_patch = patch('kafka.KafkaConsumer', autospec=True)
kafka_producer_patch.start()
kafka_consumer_patch.start()

from orders.main import app
from orders.database import Base, get_db
from orders.models import Order
from orders import kafka_producer

@pytest.fixture(autouse=True)
def stop_kafka_patch():
    """A fixture to stop the patch after the test session."""
    yield
    kafka_producer_patch.stop()
    kafka_consumer_patch.stop()


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
    from unittest.mock import MagicMock

    # Mock the kafka producer to prevent it from trying to connect
    kafka_mock = MagicMock()
    app.dependency_overrides[kafka_producer.producer] = lambda: kafka_mock

    async def override_get_db() -> AsyncGenerator:
        async with test_db() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Clear overrides after test
    app.dependency_overrides.clear()

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
async def test_order(test_db: async_sessionmaker) -> Order:
    """Fixture to create a test order."""
    async with test_db() as session:
        order = Order(
            client_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            price_amount=100.00,
            price_currency="USD"
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order
