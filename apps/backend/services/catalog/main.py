from fastapi import FastAPI
from .api.v1 import catalog
from .database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Catalog Service",
    description="This service handles the creation and management of service offerings from suppliers.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    # Create the database tables if they don't exist
    await create_tables()

# Include the API router
app.include_router(catalog.router, prefix="/api/v1/catalog", tags=["Service Catalog"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
