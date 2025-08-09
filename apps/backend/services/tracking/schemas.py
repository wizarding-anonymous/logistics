import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrackingEvent(BaseModel):
    order_id: uuid.UUID
    status: str
    notes: Optional[str] = None
    timestamp: datetime

    class Config:
        orm_mode = True
