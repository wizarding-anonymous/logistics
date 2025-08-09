from fastapi import FastAPI
from .api.v1 import rfqs
from .database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="RFQ Service",
    description="This service handles RFQs (Requests for Quotation) and offers.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    # Create the database tables if they don't exist
    await create_tables()

# Include the API router
app.include_router(rfqs.router, prefix="/api/v1/rfqs", tags=["RFQs and Offers"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
