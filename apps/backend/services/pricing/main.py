from fastapi import FastAPI

from fastapi import FastAPI
from .api.v1 import pricing

app = FastAPI(
    title="Pricing Service",
    description="This service handles price calculations and route optimization.",
    version="1.0.0"
)

app.include_router(pricing.router, prefix="/api/v1/pricing", tags=["Pricing"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
