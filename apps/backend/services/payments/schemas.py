import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from .models import InvoiceStatus, TransactionType

# =================================
# Transaction Schemas
# =================================

class Transaction(BaseModel):
    id: uuid.UUID
    transaction_type: TransactionType
    amount: float
    notes: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True

# =================================
# Payout Schemas
# =================================

class Payout(BaseModel):
    id: uuid.UUID
    supplier_organization_id: uuid.UUID
    order_id: uuid.UUID
    amount: float
    currency: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# =================================
# Invoice Schemas
# =================================

class Invoice(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    organization_id: uuid.UUID
    status: InvoiceStatus
    amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
    transactions: List[Transaction] = []

    class Config:
        orm_mode = True
