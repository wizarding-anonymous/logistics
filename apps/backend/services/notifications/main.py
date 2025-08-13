import asyncio
import threading
from fastapi import FastAPI
from . import kafka_consumer

app = FastAPI(
    title="Notifications Service",
    description="A service that consumes events and sends notifications (currently simulated via logging).",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    """
    On startup, create a separate thread for the Kafka consumer.
    The consumer uses a blocking loop, so it needs its own thread.
    """
    consumer_thread = threading.Thread(target=kafka_consumer.start_consumer, daemon=True)
    consumer_thread.start()
    print("Kafka consumer thread started.")

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
