import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .models import OrderStatus

# =================================
# Base Schemas
# =================================

class OrderBase(BaseModel):
    client_id: uuid.UUID
    supplier_id: uuid.UUID
    price_amount: float = Field(..., gt=0, description="The price of the order.")
    price_currency: str = Field(..., min_length=3, max_length=3, description="3-letter currency code (ISO 4217).")

# =================================
# Schemas for API Operations
# =================================

# Schema for creating an order from an offer
class OrderCreate(BaseModel):
    # In a real scenario, this would take an `offer_id` and the service
    # would fetch the details to create the order.
    # For this vertical slice, we'll pass the data directly.
    client_id: uuid.UUID
    supplier_id: uuid.UUID
    price_amount: float
    price_currency: str

# Schema for updating an order's status
class OrderStatusUpdate(BaseModel):
    status: OrderStatus

# =================================
# Schemas for API Responses
# =================================

# The full Order model to be returned by the API
class Order(OrderBase):
    id: uuid.UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        # This allows Pydantic to read the data from ORM models
        orm_mode = True
