import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import uuid

from chat.main import app
from chat.database import Base, get_db
from chat.models import ChatThread, Message

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

# --- Data Fixtures ---
@pytest.fixture(scope="function")
async def test_chat_thread(test_db: async_sessionmaker) -> ChatThread:
    """Fixture to create a test chat thread with messages."""
    async with test_db() as session:
        thread = ChatThread(topic="order_123")
        msg1 = Message(sender_id=uuid.uuid4(), content="Hello")
        msg2 = Message(sender_id=uuid.uuid4(), content="Hi there")
        thread.messages.extend([msg1, msg2])
        session.add(thread)
        await session.commit()
        await session.refresh(thread)
        return thread
