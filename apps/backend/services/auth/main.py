from fastapi import FastAPI
from .api.v1 import auth
from .database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Auth Service",
    description="This service handles user registration, authentication, and authorization.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    # Create the database tables if they don't exist
    await create_tables()

# Include the API router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
