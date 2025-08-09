import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models

async def get_tracking_history(db: AsyncSession, order_id: uuid.UUID):
    """
    Retrieves all tracking events for a given order, sorted by timestamp.
    """
    result = await db.execute(
        select(models.TrackingEvent)
        .where(models.TrackingEvent.order_id == order_id)
        .order_by(models.TrackingEvent.timestamp.asc())
    )
    return result.scalars().all()
