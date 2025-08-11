import uuid
from sqlalchemy import Column, String, DateTime, func, Numeric, Enum as SAEnum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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

    segments = relationship("ShipmentSegment", back_populates="order")
    status_history = relationship("StatusHistory", back_populates="order")
    review = relationship("Review", uselist=False, back_populates="order") # One-to-one

    def __repr__(self):
        return f"<Order(id={self.id}, status='{self.status}')>"

class ShipmentSegment(Base):
    __tablename__ = "order_shipment_segments"
    id = Column(Integer, primary_key=True) # Simple integer PK for this table
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    origin_address = Column(String, nullable=False)
    destination_address = Column(String, nullable=False)
    transport_type = Column(String, nullable=True)

    order = relationship("Order", back_populates="segments")

class StatusHistory(Base):
    __tablename__ = "order_status_history"
    id = Column(Integer, primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    status = Column(SAEnum(OrderStatus), nullable=False)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    order = relationship("Order", back_populates="status_history")

class Review(Base):
    __tablename__ = "order_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, unique=True) # One review per order

    # The user/org that wrote the review
    reviewer_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    rating = Column(Integer, nullable=False) # e.g., 1 to 5 stars
    comment = Column(Text, nullable=True)

    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    order = relationship("Order")
