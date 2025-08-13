import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service, security
from ...database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Dispute, status_code=status.HTTP_201_CREATED)
async def open_dispute_endpoint(
    dispute_in: schemas.DisputeCreate,
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.get_current_user_context),
    _ = Depends(security.require_permission("disputes:create")),
):
    new_dispute = await service.open_dispute(db, dispute_in, user_context)
    if new_dispute == "not_found":
        raise HTTPException(status_code=404, detail="Order not found.")
    if new_dispute == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to open a dispute for this order.")
    if new_dispute == "conflict":
        raise HTTPException(status_code=409, detail="A dispute for this order already exists.")
    return new_dispute

@router.get("/by-order/{order_id}", response_model=schemas.Dispute)
async def get_dispute_by_order_endpoint(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.get_current_user_context),
):
    dispute = await service.get_dispute_by_order_id(db, order_id, user_context)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found for this order.")
    if dispute == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to view this dispute.")
    return dispute

@router.get("/open", response_model=List[schemas.Dispute])
async def list_open_disputes_endpoint(
    db: AsyncSession = Depends(get_db),
    _ = Depends(security.require_permission("disputes:manage")),
):
    """
    Get a list of all open disputes for moderation.
    """
    return await service.list_open_disputes(db)

@router.post("/{dispute_id}/messages", response_model=schemas.DisputeMessage)
async def add_dispute_message_endpoint(
    dispute_id: uuid.UUID,
    message_in: schemas.DisputeMessageCreate,
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.get_current_user_context),
):
    new_message = await service.add_message_to_dispute(db, dispute_id, message_in, user_context)
    if not new_message:
        raise HTTPException(status_code=404, detail="Dispute not found.")
    if new_message == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to post messages in this dispute.")
    return new_message

@router.post("/{dispute_id}/resolve", response_model=schemas.Dispute)
async def resolve_dispute_endpoint(
    dispute_id: uuid.UUID,
    resolution_in: schemas.DisputeResolution,
    db: AsyncSession = Depends(get_db),
    _ = Depends(security.require_permission("disputes:manage")),
):
    resolved_dispute = await service.resolve_dispute(db, dispute_id, resolution_in)
    if not resolved_dispute:
        raise HTTPException(status_code=404, detail="Dispute not found.")
    return resolved_dispute
