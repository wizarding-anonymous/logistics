import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service
from ...database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    order: schemas.OrderCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new order.
    """
    return await service.create_order(db=db, order=order)

@router.get("/", response_model=List[schemas.Order])
async def list_orders_endpoint(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    List all orders with pagination.
    """
    orders = await service.get_orders(db, skip=skip, limit=limit)
    return orders

@router.get("/{order_id}", response_model=schemas.Order)
async def get_order_endpoint(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a single order by its ID.
    """
    db_order = await service.get_order_by_id(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.patch("/{order_id}/status", response_model=schemas.Order)
async def update_order_status_endpoint(
    order_id: uuid.UUID,
    status_update: schemas.OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an order's status.
    """
    updated_order = await service.update_order_status(
        db, order_id=order_id, status_update=status_update
    )
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order
