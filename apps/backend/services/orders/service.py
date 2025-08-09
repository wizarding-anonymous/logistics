import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models, schemas, kafka_producer

async def get_order_by_id(db: AsyncSession, order_id: uuid.UUID):
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    return result.scalars().first()

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Order).offset(skip).limit(limit))
    return result.scalars().all()

async def create_order(db: AsyncSession, order: schemas.OrderCreate):
    db_order = models.Order(
        client_id=order.client_id,
        supplier_id=order.supplier_id,
        price_amount=order.price_amount,
        price_currency=order.price_currency,
        status=models.OrderStatus.CREATED
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def update_order_status(db: AsyncSession, order_id: uuid.UUID, status_update: schemas.OrderStatusUpdate):
    db_order = await get_order_by_id(db, order_id)
    if not db_order:
        return None

    db_order.status = status_update.status
    await db.commit()
    await db.refresh(db_order)

    # If POD is confirmed, publish an event for the payments service
    if db_order.status == models.OrderStatus.POD_CONFIRMED:
        event_payload = {
            "order_id": str(db_order.id),
            "client_organization_id": str(db_order.client_id),
            "supplier_organization_id": str(db_order.supplier_id),
            "price_amount": float(db_order.price_amount),
            "price_currency": db_order.price_currency,
        }
        kafka_producer.publish_pod_confirmed(event_payload)

    return db_order
