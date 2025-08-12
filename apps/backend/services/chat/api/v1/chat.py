from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import uuid

from ... import schemas, service
from ...database import get_db
from ...connection_manager import manager
# TODO: Add a proper security dependency to get user context from token
# from ...security import get_current_user_context

router = APIRouter()

@router.get("/history/{topic}", response_model=schemas.ChatThread)
async def get_chat_history(
    topic: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the message history for a specific chat topic.
    """
    return await service.get_or_create_thread_by_topic(db, topic)

@router.websocket("/ws/{topic}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    topic: str,
    user_id: str, # In a real app, this would come from the decoded token
    db: AsyncSession = Depends(get_db)
):
    await manager.connect(websocket, topic)
    try:
        while True:
            data = await websocket.receive_text()
            # Create message in DB
            message_data = json.loads(data)
            new_message = await service.create_message(
                db,
                topic=topic,
                sender_id=uuid.UUID(user_id),
                content=message_data['content']
            )
            # Broadcast the new message to all clients in the same topic
            await manager.broadcast(new_message.json(), topic)
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)
        print(f"Client {user_id} disconnected from topic {topic}")
