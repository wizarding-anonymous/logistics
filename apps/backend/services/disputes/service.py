import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from . import models, schemas

async def get_dispute_by_order_id(db: AsyncSession, order_id: uuid.UUID):
    result = await db.execute(
        select(models.Dispute)
        .where(models.Dispute.order_id == order_id)
        .options(selectinload(models.Dispute.messages))
    )
    return result.scalars().first()

async def open_dispute(db: AsyncSession, dispute_in: schemas.DisputeCreate, user_context: dict):
    # Check if a dispute for this order already exists
    existing_dispute = await get_dispute_by_order_id(db, dispute_in.order_id)
    if existing_dispute:
        return None # Indicate that it already exists

    # Create the dispute
    new_dispute = models.Dispute(
        order_id=dispute_in.order_id,
        opened_by_id=user_context["user_id"]
    )

    # Create the initial message
    initial_message = models.DisputeMessage(
        sender_id=user_context["user_id"],
        content=dispute_in.reason
    )
    new_dispute.messages.append(initial_message)

    db.add(new_dispute)
    await db.commit()
    await db.refresh(new_dispute)
    return new_dispute

async def add_message_to_dispute(db: AsyncSession, dispute_id: uuid.UUID, message_in: schemas.DisputeMessageCreate, user_context: dict):
    dispute = await db.get(models.Dispute, dispute_id)
    if not dispute:
        return None

    # TODO: Add authz check to ensure user is part of the dispute (client, supplier, or admin)

    new_message = models.DisputeMessage(
        dispute_id=dispute_id,
        sender_id=user_context["user_id"],
        content=message_in.content
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

async def resolve_dispute(db: AsyncSession, dispute_id: uuid.UUID, resolution_in: schemas.DisputeResolution):
    dispute = await db.get(models.Dispute, dispute_id)
    if not dispute:
        return None

    dispute.status = models.DisputeStatus.RESOLVED
    dispute.resolution = resolution_in.resolution
    dispute.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(dispute)
    return dispute
