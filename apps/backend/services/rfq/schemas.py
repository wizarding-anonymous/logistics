import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .models import RFQStatus, OfferStatus

# =================================
# Offer Schemas
# =================================

class OfferBase(BaseModel):
    price_amount: float = Field(..., gt=0)
    price_currency: str = Field(..., min_length=3, max_length=3)
    notes: Optional[str] = None

class OfferCreate(OfferBase):
    pass

class Offer(OfferBase):
    id: uuid.UUID
    rfq_id: uuid.UUID
    supplier_organization_id: uuid.UUID
    status: OfferStatus
    created_at: datetime

    class Config:
        orm_mode = True

# =================================
# Cargo & Segment Schemas
# =================================

class CargoBase(BaseModel):
    description: str
    weight_kg: Optional[float] = None
    volume_cbm: Optional[float] = None
    pallet_count: Optional[int] = None
    value: Optional[float] = None
    value_currency: Optional[str] = None
    hazard_class: Optional[str] = None
    temperature_control: Optional[str] = None

class CargoCreate(CargoBase):
    pass

class Cargo(CargoBase):
    id: uuid.UUID
    class Config:
        orm_mode = True

class ShipmentSegmentBase(BaseModel):
    origin_address: str
    destination_address: str

class ShipmentSegmentCreate(ShipmentSegmentBase):
    pass

class ShipmentSegment(ShipmentSegmentBase):
    id: uuid.UUID
    sequence: int
    class Config:
        orm_mode = True

# =================================
# RFQ Schemas
# =================================

class RFQBase(BaseModel):
    # Tender-specific fields
    incoterms: Optional[str] = None
    deadline: Optional[datetime] = None
    tender_type: str = 'open'

class RFQCreate(RFQBase):
    cargo: CargoCreate
    segments: List[ShipmentSegmentCreate]

class RFQ(RFQBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    status: RFQStatus
    created_at: datetime
    offers: List[Offer] = []
    cargo: Cargo
    segments: List[ShipmentSegment]

    class Config:
        orm_mode = True
