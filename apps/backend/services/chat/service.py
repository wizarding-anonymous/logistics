import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models, schemas

async def get_or_create_thread_by_topic(db: AsyncSession, topic: str) -> models.ChatThread:
    """
    Retrieves a chat thread by its topic. If it doesn't exist, it creates one.
    """
    result = await db.execute(
        select(models.ChatThread)
        .where(models.ChatThread.topic == topic)
        .options(selectinload(models.ChatThread.messages))
    )
    thread = result.scalars().first()

    if not thread:
        thread = models.ChatThread(topic=topic)
        db.add(thread)
        await db.commit()
        await db.refresh(thread)

    return thread

import json
from typing import Dict, Any

async def create_message(db: AsyncSession, topic: str, sender_id: uuid.UUID, content: Dict[str, Any]) -> models.Message:
    """
    Creates a new message and adds it to a chat thread.
    The content is a dictionary that will be stored as a JSON string.
    e.g., {"type": "text", "body": "Hello world"}
    e.g., {"type": "file", "filename": "invoice.pdf", "url": "..."}
    """
    thread = await get_or_create_thread_by_topic(db, topic)

    message = models.Message(
        thread_id=thread.id,
        sender_id=sender_id,
        content=json.dumps(content)  # Serialize dict to JSON string
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
