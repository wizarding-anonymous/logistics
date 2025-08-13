from fastapi import APIRouter, Depends
from .... import schemas, service

router = APIRouter()

@router.post("/calculate", response_model=schemas.PriceCalculationResponse)
async def calculate_price_endpoint(
    request: schemas.PriceCalculationRequest
):
    """
    Calculates a price based on shipment details.
    """
    # This will call the service function that contains the calculation logic.
    return await service.calculate_price(request)

@router.post("/compare-prices", response_model=schemas.PriceComparisonResponse)
async def compare_prices_endpoint(
    request: schemas.PriceComparisonRequest
):
    """
    Calculates prices for a list of suppliers and returns them for comparison.
    """
    # This will call the service function that contains the comparison logic.
    # The implementation will be done in the next step.
    return await service.compare_prices(request)
