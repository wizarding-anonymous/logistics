import logging
import threading
from fastapi import FastAPI
from .api.v1 import tracking
from .database import Base, engine
from .kafka_consumer import consume_order_events

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Tracking Service",
    description="This service consumes order events and provides tracking history.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    # Create the database tables if they don't exist
    await create_tables()

    # Start the Kafka consumer in a background thread
    logging.info("Starting Kafka consumer thread...")
    consumer_thread = threading.Thread(target=consume_order_events, daemon=True)
    consumer_thread.start()

# Include the API router
app.include_router(tracking.router, prefix="/api/v1", tags=["Tracking"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
