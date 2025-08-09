import asyncio
from fastapi import FastAPI
from .api.v1 import orders
from .database import Base, engine
from . import kafka_consumer

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Orders Service",
    description="This service handles the creation and management of orders.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    # Create the database tables if they don't exist
    await create_tables()
    # Start the Kafka consumer in the background
    loop = asyncio.get_event_loop()
    loop.create_task(kafka_consumer.consume_events())


# Include the API router
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
