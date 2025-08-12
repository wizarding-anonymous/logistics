import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# =================================
# Message Schemas
# =================================

class DisputeMessageBase(BaseModel):
    content: str

class DisputeMessageCreate(DisputeMessageBase):
    pass

class DisputeMessage(DisputeMessageBase):
    id: uuid.UUID
    dispute_id: uuid.UUID
    sender_id: uuid.UUID
    timestamp: datetime
    class Config:
        orm_mode = True

# =================================
# Dispute Schemas
# =================================

class DisputeCreate(BaseModel):
    order_id: uuid.UUID
    reason: str # The initial message from the user opening the dispute

class Dispute(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    opened_by_id: uuid.UUID
    status: str
    resolution: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    messages: List[DisputeMessage] = []
    class Config:
        orm_mode = True

class DisputeResolution(BaseModel):
    resolution: str = Field(..., description="The admin's final decision and notes.")
