import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service, security
from ...database import get_db

router = APIRouter()

@router.get("/orders", response_model=List[schemas.Order])
async def list_orders_endpoint(
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    """
    List all orders relevant to the user's organization.
    """
    # TODO: Modify service layer to filter orders by org_id
    return await service.list_orders(db)

@router.get("/orders/{order_id}", response_model=schemas.Order)
async def get_order_endpoint(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    """
    Get a single order by its ID.
    TODO: Add authz check to ensure user's org is either client or supplier.
    """
    db_order = await service.get_order_by_id(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    # A simple authz check
    if db_order.client_id != user_context["org_id"] and db_order.supplier_id != user_context["org_id"]:
         raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return db_order

@router.patch("/orders/{order_id}/status", response_model=schemas.Order)
async def update_order_status_endpoint(
    order_id: uuid.UUID,
    status_update: schemas.OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    """
    Update an order's status. This action is protected and can only be performed
    by the assigned supplier.
    """
    updated_order = await service.update_order_status(
        db, order_id=order_id, status_update=status_update, user_context=user_context
    )
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if updated_order == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to update this order's status")
    return updated_order

@router.post("/orders/{order_id}/review", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
async def create_review_endpoint(
    order_id: uuid.UUID,
    review_in: schemas.ReviewCreate,
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    """
    Allows a client to submit a review for a completed order.
    """
    new_review = await service.create_review_for_order(
        db, order_id=order_id, review_in=review_in, user_context=user_context
    )

    if new_review is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if new_review == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to review this order")
    if new_review == "not_completed":
        raise HTTPException(status_code=400, detail="Order is not completed yet")
    if new_review == "already_reviewed":
        raise HTTPException(status_code=400, detail="This order has already been reviewed")

    return new_review
