from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import uuid

from ... import schemas, service, security
from ...database import get_db
from ...connection_manager import manager

router = APIRouter()

@router.get("/history/{topic}", response_model=schemas.ChatThread)
async def get_chat_history(
    topic: str,
    db: AsyncSession = Depends(get_db)
    # TODO: Add authz check to ensure user has access to this topic (e.g., is part of the order)
):
    """
    Get the message history for a specific chat topic.
    """
    return await service.get_or_create_thread_by_topic(db, topic)

@router.websocket("/ws/{topic}")
async def websocket_endpoint(
    websocket: WebSocket,
    topic: str,
    user_context: security.UserContext = Depends(security.get_user_context_from_query),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat.
    Authenticates using a 'token' query parameter.
    e.g., ws://localhost/api/v1/chat/ws/some_topic?token=xxxx
    """
    # TODO: Further authorization to check if user_context.org_id can access this topic
    await manager.connect(websocket, topic)
    try:
        while True:
            data = await websocket.receive_text()
            # The entire data is the JSON message content
            message_content = json.loads(data)

            new_message = await service.create_message(
                db,
                topic=topic,
                sender_id=user_context.id,
                content=message_content
            )
            # Broadcast the new message (which is a JSON string) to all clients
            await manager.broadcast(new_message.content, topic)
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)
        print(f"Client {user_context.id} disconnected from topic {topic}")
