import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Numeric, ForeignKey, Enum as SAEnum
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

    origin_address = Column(String, nullable=False)
    destination_address = Column(String, nullable=False)

    cargo_description = Column(String, nullable=False)
    cargo_weight_kg = Column(Numeric(10, 2), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    offers = relationship("Offer", back_populates="rfq")

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
