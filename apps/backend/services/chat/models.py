import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # This could be linked to an order_id, rfq_id, etc.
    # For now, a generic topic seems flexible.
    topic = Column(String, nullable=False, index=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id"), nullable=False)

    sender_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content = Column(Text, nullable=False)

    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    thread = relationship("ChatThread", back_populates="messages")
