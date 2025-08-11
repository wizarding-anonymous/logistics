from fastapi import FastAPI
from .api.v1 import chat
from .database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Chat Service",
    description="This service handles real-time chat and message history.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    await create_tables()

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
