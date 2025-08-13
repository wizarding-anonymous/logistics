import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .models import OrderStatus

# =================================
# Sub-Schemas
# =================================

class ShipmentSegment(BaseModel):
    origin_address: str
    destination_address: str
    transport_type: Optional[str] = None
    class Config:
        orm_mode = True

class StatusHistory(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None
    timestamp: datetime
    class Config:
        orm_mode = True

# =================================
# Schemas for API Operations
# =================================

# Per OpenAPI spec, this is the ideal create schema
class OrderCreate(BaseModel):
    offer_id: uuid.UUID
    # In a real implementation, the service would call the RFQ service
    # to get all other details from this offer_id.
    # For now, we might pass them in directly to decouple the services in this phase.

# Schema for updating an order's status
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None

# =================================
# Schemas for API Responses
# =================================

class ReviewBase(BaseModel):
    rating: int = Field(..., gt=0, le=5, description="Rating from 1 to 5 stars.")
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: uuid.UUID
    order_id: uuid.UUID
    reviewer_id: uuid.UUID
    timestamp: datetime
    class Config:
        orm_mode = True

# The full Order model to be returned by the API
class Order(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    supplier_id: uuid.UUID
    price_amount: float
    price_currency: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    segments: List[ShipmentSegment] = []
    status_history: List[StatusHistory] = []
    review: Optional[Review] = None

    class Config:
        # This allows Pydantic to read the data from ORM models
        orm_mode = True


# --- Schemas for Order Update ---

class ShipmentSegmentUpdate(BaseModel):
    # We need an ID to identify which segment to update
    id: int
    origin_address: Optional[str] = None
    destination_address: Optional[str] = None

class OrderUpdate(BaseModel):
    segments: Optional[List[ShipmentSegmentUpdate]] = None
