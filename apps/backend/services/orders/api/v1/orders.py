import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service
from ...database import get_db

router = APIRouter()

# In a real app, this dependency would be shared across services in a common library
# and would provide a richer user context (user_id, org_id, roles, etc.)
def get_current_user_id_placeholder() -> uuid.UUID:
    # Placeholder: replace with actual token decoding and user context logic
    return uuid.uuid4()

@router.post("/orders", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    order_in: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    # user_id: uuid.UUID = Depends(get_current_user_id_placeholder) # Placeholder
):
    """
    Creates a new order from an accepted offer.
    """
    # The service layer currently mocks the data fetching from the offer_id
    return await service.create_order(db=db, order_in=order_in)

@router.get("/orders", response_model=List[schemas.Order])
async def list_orders_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    # user_id: uuid.UUID = Depends(get_current_user_id_placeholder)
):
    """
    List all orders with pagination.
    TODO: Add filtering by status, client_id, supplier_id, etc.
    TODO: Add authz to only show relevant orders to the user.
    """
    return await service.list_orders(db, skip=skip, limit=limit)

@router.get("/orders/{order_id}", response_model=schemas.Order)
async def get_order_endpoint(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # user_id: uuid.UUID = Depends(get_current_user_id_placeholder)
):
    """
    Get a single order by its ID.
    TODO: Add authz check.
    """
    db_order = await service.get_order_by_id(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.patch("/orders/{order_id}/status", response_model=schemas.Order)
async def update_order_status_endpoint(
    order_id: uuid.UUID,
    status_update: schemas.OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    # user_id: uuid.UUID = Depends(get_current_user_id_placeholder)
):
    """
    Update an order's status. This action creates a new entry in the order's status history.
    TODO: Add authz to check if the user is allowed to perform this status transition (e.g., supplier can mark as 'in_transit', client can 'confirm_pod').
    """
    updated_order = await service.update_order_status(
        db, order_id=order_id, status_update=status_update
    )
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order
