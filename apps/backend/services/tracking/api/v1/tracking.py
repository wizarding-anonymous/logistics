import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service
from ...database import get_db

router = APIRouter()

@router.get("/tracking/{order_id}", response_model=List[schemas.TrackingEvent])
async def get_tracking_history_endpoint(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authz check to ensure user is allowed to view this order's tracking
):
    """
    Get the full tracking history for a specific order.
    """
    history = await service.get_tracking_history(db, order_id=order_id)
    if not history:
        # Return an empty list and a 200, as no history is not an error.
        # Alternatively, could check if order exists and 404 if not.
        # For a decoupled service, this is simpler.
        return []
    return history
