import httpx
from . import schemas
from decimal import Decimal

CATALOG_SERVICE_URL = "http://catalog_service:8000"

async def get_tariffs_from_catalog(supplier_id: str, service_type: str):
    """Calls the catalog service to get tariffs."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CATALOG_SERVICE_URL}/api/v1/catalog/internal/tariffs",
                params={"supplier_org_id": supplier_id, "service_type": service_type}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error fetching tariffs: {e.response.status_code} {e.response.text}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while fetching tariffs: {e}")
            return []

async def calculate_price(request: schemas.PriceCalculationRequest) -> schemas.PriceCalculationResponse:
    """
    Calculates a price based on real tariffs fetched from the catalog service.
    """
    breakdown = {}

    # 1. Fetch tariffs from Catalog service
    tariffs = await get_tariffs_from_catalog(str(request.supplier_id), request.service_type)

    # Find the relevant tariff (e.g., per kg). A real app would have more complex logic.
    per_kg_tariff = next((t for t in tariffs if t.get("unit") == "per_kg"), None)

    # 2. Base Rate (could also be a tariff type)
    base_rate = Decimal("100.00")
    breakdown["base_rate"] = float(base_rate)

    # 3. Weight-based charge using the dynamic tariff
    if per_kg_tariff:
        rate_per_kg = Decimal(str(per_kg_tariff["price"]))
        weight_charge = Decimal(str(request.weight_kg)) * rate_per_kg
        breakdown["weight_charge"] = {
            "rate": float(rate_per_kg),
            "total": float(weight_charge)
        }
    else:
        # Fallback or error if no tariff is found
        weight_charge = Decimal("0.00")
        breakdown["weight_charge"] = "No 'per_kg' tariff found."

    # 4. Surcharges (can remain hardcoded for now)
    surcharges = Decimal("0.00")
    if request.temperature_control and request.temperature_control != "ambient":
        temp_surcharge = Decimal("75.00")
        surcharges += temp_surcharge
        breakdown["temperature_surcharge"] = float(temp_surcharge)

    if request.service_type.lower() == "air":
        air_surcharge = Decimal("200.00")
        surcharges += air_surcharge
        breakdown["air_freight_surcharge"] = float(air_surcharge)

    # 5. Total Calculation
    total_amount = base_rate + weight_charge + surcharges

    return schemas.PriceCalculationResponse(
        calculated_amount=float(total_amount),
        currency="USD", # Assuming USD for now, could come from tariff
        breakdown=breakdown
    )

import asyncio

async def compare_prices(request: schemas.PriceComparisonRequest) -> schemas.PriceComparisonResponse:
    """
    Compares prices from multiple suppliers for the same shipment.
    """

    async def get_price_for_supplier(supplier_id):
        """Helper function to calculate price for a single supplier."""
        calc_request = schemas.PriceCalculationRequest(
            supplier_id=supplier_id,
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            weight_kg=request.weight_kg,
            service_type=request.service_type,
            temperature_control=request.temperature_control
        )
        price_response = await calculate_price(calc_request)
        return schemas.PricedOption(supplier_id=supplier_id, price=price_response)

    # Run all price calculations concurrently
    tasks = [get_price_for_supplier(sid) for sid in request.supplier_ids]
    priced_options = await asyncio.gather(*tasks)

    return schemas.PriceComparisonResponse(options=priced_options)
