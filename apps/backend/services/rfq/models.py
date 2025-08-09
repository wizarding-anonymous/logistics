import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Numeric, ForeignKey, Enum as SAEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class RFQStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed" # An offer has been accepted
    CANCELLED = "cancelled"

class OfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class RFQ(Base):
    __tablename__ = "rfqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(SAEnum(RFQStatus), nullable=False, default=RFQStatus.OPEN)

    # Tender-specific fields
    incoterms = Column(String(3), nullable=True)
    deadline = Column(DateTime, nullable=True)
    tender_type = Column(String, default='open') # 'open' or 'hidden'

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    offers = relationship("Offer", back_populates="rfq")
    cargo = relationship("Cargo", back_populates="rfq", uselist=False) # One-to-one
    segments = relationship("ShipmentSegment", back_populates="rfq") # One-to-many

class Cargo(Base):
    __tablename__ = "cargo"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False)

    description = Column(String, nullable=False)
    weight_kg = Column(Numeric(10, 2), nullable=True)
    volume_cbm = Column(Numeric(10, 3), nullable=True)
    pallet_count = Column(Integer, nullable=True)
    value = Column(Numeric(12, 2), nullable=True)
    value_currency = Column(String(3), nullable=True)
    hazard_class = Column(String, nullable=True)
    temperature_control = Column(String, nullable=True)

    rfq = relationship("RFQ", back_populates="cargo")

class ShipmentSegment(Base):
    __tablename__ = "shipment_segments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False)

    sequence = Column(Integer, nullable=False) # e.g., 1, 2, 3
    origin_address = Column(String, nullable=False)
    destination_address = Column(String, nullable=False)

    rfq = relationship("RFQ", back_populates="segments")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False)
    supplier_organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), nullable=False)

    notes = Column(String, nullable=True)
    status = Column(SAEnum(OfferStatus), nullable=False, default=OfferStatus.PENDING)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    rfq = relationship("RFQ", back_populates="offers")
