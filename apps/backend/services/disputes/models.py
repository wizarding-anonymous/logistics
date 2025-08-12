import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"

class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)

    # The user/org that opened the dispute
    opened_by_id = Column(UUID(as_uuid=True), nullable=False)

    status = Column(SAEnum(DisputeStatus), nullable=False, default=DisputeStatus.OPEN)
    resolution = Column(Text, nullable=True) # The final decision by the admin

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    messages = relationship("DisputeMessage", back_populates="dispute", cascade="all, delete-orphan")

class DisputeMessage(Base):
    __tablename__ = "dispute_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id"), nullable=False)

    sender_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content = Column(Text, nullable=False)

    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    dispute = relationship("Dispute", back_populates="messages")
