import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# =================================
# Tariff Schemas
# =================================

class TariffBase(BaseModel):
    price: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    unit: str

class TariffCreate(TariffBase):
    pass

class Tariff(TariffBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

# =================================
# Service Offering Schemas
# =================================

class ServiceOfferingBase(BaseModel):
    name: str
    description: Optional[str] = None
    service_type: str
    is_active: bool = True

class ServiceOfferingCreate(ServiceOfferingBase):
    tariffs: List[TariffCreate] = []

class ServiceOffering(ServiceOfferingBase):
    id: uuid.UUID
    supplier_organization_id: uuid.UUID
    tariffs: List[Tariff] = []

    class Config:
        orm_mode = True
