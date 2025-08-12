import asyncio
from fastapi import FastAPI
from .api.v1 import search
from . import kafka_consumer, es_client

app = FastAPI(
    title="Search Service",
    description="This service provides a unified search interface using Elasticsearch.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    # Verify connection to Elasticsearch
    if not es_client.es_client.ping():
        raise ConnectionError("Could not connect to Elasticsearch")

    # Start the Kafka consumer in the background
    loop = asyncio.get_event_loop()
    loop.create_task(kafka_consumer.consume_events())

app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
