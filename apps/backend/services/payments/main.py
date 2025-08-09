import asyncio
from fastapi import FastAPI
from .api.v1 import payments
from .database import Base, engine
from . import kafka_consumer

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Payments Service",
    description="This service handles invoices, transactions, and payouts.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    await create_tables()
    loop = asyncio.get_event_loop()
    loop.create_task(kafka_consumer.consume_events())

app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
