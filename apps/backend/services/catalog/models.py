import uuid
from sqlalchemy import Column, String, DateTime, func, Numeric, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class ServiceOffering(Base):
    __tablename__ = "service_offerings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    service_type = Column(String, nullable=False) # e.g., 'FTL', 'LTL', 'Warehouse'
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    tariffs = relationship("Tariff", back_populates="service_offering")

class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_offering_id = Column(UUID(as_uuid=True), ForeignKey("service_offerings.id"), nullable=False)

    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    unit = Column(String, nullable=False) # e.g., 'per_kg', 'per_pallet', 'fixed'

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    service_offering = relationship("ServiceOffering", back_populates="tariffs")
