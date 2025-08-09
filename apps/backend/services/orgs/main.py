from fastapi import FastAPI
from .api.v1 import orgs, teams
from .database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Organizations Service",
    description="This service handles creating and managing organizations, teams, and members.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    # Create the database tables if they don't exist
    await create_tables()

# Include the API routers
app.include_router(orgs.router, prefix="/api/v1/orgs", tags=["Organizations"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
