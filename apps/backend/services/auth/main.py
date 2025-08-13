from fastapi import FastAPI
from .api.v1 import auth
from .database import Base, engine
from .logging_config import setup_logging
from .rate_limiter import RateLimiterMiddleware
from .redis_client import redis_client

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Auth Service",
    description="This service handles user registration, authentication, and authorization with enhanced security features.",
    version="2.0.0"
)

# Add rate limiting middleware
app.add_middleware(RateLimiterMiddleware)

@app.on_event("startup")
async def on_startup():
    # Configure logging
    setup_logging()
    # Create the database tables if they don't exist
    await create_tables()
    # Initialize Redis connection
    await redis_client.connect()

@app.on_event("shutdown")
async def on_shutdown():
    # Close Redis connection
    await redis_client.disconnect()

# Include the API router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok", "version": "2.0.0"}

@app.get("/health/redis", tags=["Health"])
async def redis_health_check():
    """
    Redis health check endpoint.
    """
    try:
        await redis_client.set("health_check", "ok", 10)
        result = await redis_client.get("health_check")
        return {"status": "ok", "redis": "connected" if result == "ok" else "error"}
    except Exception as e:
        return {"status": "error", "redis": "disconnected", "error": str(e)}
