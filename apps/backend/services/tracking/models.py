import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    status = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    # We don't need a relationship back to an Order model here,
    # as this service is read-only and aggregates data.

    def __repr__(self):
        return f"<TrackingEvent(order_id={self.order_id}, status='{self.status}')>"
