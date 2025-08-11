from fastapi import FastAPI
from .api.v1 import admin
from .database import Base, engine

async def create_tables():
    # This is for initial setup; in a real app with Alembic, this might not be needed.
    # Note: This will not create tables from other services.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Admin Service",
    description="This service handles administrative tasks like KYC verification.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    await create_tables()

app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
