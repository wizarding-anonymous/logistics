from fastapi import FastAPI
from .api.v1 import disputes
from .database import Base, engine

app = FastAPI(
    title="Disputes Service",
    description="This service handles disputes between clients and suppliers.",
    version="1.0.0"
)

# Note: We are not running create_tables on startup here,
# as we will rely on Alembic to manage the schema.

app.include_router(disputes.router, prefix="/api/v1/disputes", tags=["Disputes"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
