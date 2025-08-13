import uuid
from pydantic import BaseModel, Field
from typing import Optional

class PriceCalculationRequest(BaseModel):
    supplier_id: uuid.UUID
    origin_address: str
    destination_address: str
    weight_kg: float = Field(..., gt=0)
    volume_cbm: Optional[float] = Field(None, gt=0)
    service_type: str # e.g., 'FTL', 'LTL', 'Air'
    temperature_control: Optional[str] = None # e.g., 'ambient', 'chilled'

class PriceCalculationResponse(BaseModel):
    calculated_amount: float
    currency: str
    breakdown: dict

class PriceComparisonRequest(BaseModel):
    supplier_ids: List[uuid.UUID]
    origin_address: str
    destination_address: str
    weight_kg: float = Field(..., gt=0)
    service_type: str
    temperature_control: Optional[str] = None

class PricedOption(BaseModel):
    supplier_id: uuid.UUID
    price: PriceCalculationResponse

class PriceComparisonResponse(BaseModel):
    options: List[PricedOption]
