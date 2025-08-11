import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import List

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: uuid.UUID
    thread_id: uuid.UUID
    sender_id: uuid.UUID
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatThread(BaseModel):
    id: uuid.UUID
    topic: str
    created_at: datetime
    messages: List[Message] = []

    class Config:
        orm_mode = True
