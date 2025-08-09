import uuid
from sqlalchemy import Column, String, DateTime, func, Numeric, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import enum

class OrderStatus(str, enum.Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    POD_CONFIRMED = "pod_confirmed"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    status = Column(SAEnum(OrderStatus), nullable=False, default=OrderStatus.CREATED)

    # Using Numeric for precision with money
    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Order(id={self.id}, status='{self.status}')>"
