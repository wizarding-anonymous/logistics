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
    user_context: dict = Depends(security.get_current_user_context),
):
    # TODO: Authz check to ensure user is either the client or supplier for the order_id
    new_dispute = await service.open_dispute(db, dispute_in, user_context)
    if not new_dispute:
        raise HTTPException(status_code=400, detail="A dispute for this order already exists.")
    return new_dispute

@router.get("/by-order/{order_id}", response_model=schemas.Dispute)
async def get_dispute_by_order_endpoint(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    # TODO: Authz check
    dispute = await service.get_dispute_by_order_id(db, order_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found for this order.")
    return dispute

@router.post("/{dispute_id}/messages", response_model=schemas.DisputeMessage)
async def add_dispute_message_endpoint(
    dispute_id: uuid.UUID,
    message_in: schemas.DisputeMessageCreate,
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    new_message = await service.add_message_to_dispute(db, dispute_id, message_in, user_context)
    if not new_message:
        raise HTTPException(status_code=404, detail="Dispute not found.")
    return new_message

@router.post("/{dispute_id}/resolve", response_model=schemas.Dispute)
async def resolve_dispute_endpoint(
    dispute_id: uuid.UUID,
    resolution_in: schemas.DisputeResolution,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role), # Assuming this dep exists
):
    # TODO: The require_admin_role dep needs to be defined in security.py
    resolved_dispute = await service.resolve_dispute(db, dispute_id, resolution_in)
    if not resolved_dispute:
        raise HTTPException(status_code=404, detail="Dispute not found.")
    return resolved_dispute
