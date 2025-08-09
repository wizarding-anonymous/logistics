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

    # Extended attributes
    sla_description: Optional[str] = None
    geo_restrictions: Optional[str] = None
    allowed_hazard_classes: Optional[List[str]] = None
    temperature_control: Optional[str] = None

class ServiceOfferingCreate(ServiceOfferingBase):
    tariffs: List[TariffCreate] = []

class ServiceOfferingUpdate(ServiceOfferingBase):
    name: Optional[str] = None
    service_type: Optional[str] = None
    tariffs: Optional[List[TariffCreate]] = None

from decimal import Decimal

class ServiceOffering(ServiceOfferingBase):
    id: uuid.UUID
    supplier_organization_id: uuid.UUID
    tariffs: List[Tariff] = []

    # Read-only rating fields
    rating_avg: Optional[Decimal] = None
    rating_count: int = 0

    class Config:
        orm_mode = True
