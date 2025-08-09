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
# RFQ Schemas
# =================================

class RFQBase(BaseModel):
    origin_address: str
    destination_address: str
    cargo_description: str
    cargo_weight_kg: Optional[float] = None

class RFQCreate(RFQBase):
    pass

class RFQ(RFQBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    status: RFQStatus
    created_at: datetime
    offers: List[Offer] = []

    class Config:
        orm_mode = True
