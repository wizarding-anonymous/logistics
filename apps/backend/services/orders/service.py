import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models, schemas, kafka_producer

# A mock function to simulate fetching offer details from the RFQ service
async def mock_get_offer_details(offer_id: uuid.UUID):
    # In a real scenario, this would be an HTTP call to the RFQ service.
    # For now, it returns dummy data.
    return {
        "client_id": uuid.uuid4(),
        "supplier_id": uuid.uuid4(),
        "price_amount": 1234.56,
        "price_currency": "RUB",
        "segments": [
            {"origin_address": "Moscow, RU", "destination_address": "St. Petersburg, RU", "transport_type": "auto_ftl"}
        ]
    }

async def create_order(db: AsyncSession, order_in: schemas.OrderCreate):
    # 1. Fetch details from RFQ service using offer_id (mocked for now)
    offer_details = await mock_get_offer_details(order_in.offer_id)

    # 2. Create the Order instance
    db_order = models.Order(
        id=uuid.uuid4(), # Generate ID here to link children
        client_id=offer_details["client_id"],
        supplier_id=offer_details["supplier_id"],
        price_amount=offer_details["price_amount"],
        price_currency=offer_details["price_currency"],
        status=models.OrderStatus.CREATED
    )

    # 3. Create ShipmentSegments
    for segment_data in offer_details.get("segments", []):
        db_segment = models.ShipmentSegment(order_id=db_order.id, **segment_data)
        db.add(db_segment)

    # 4. Create the initial StatusHistory entry
    db_status_history = models.StatusHistory(
        order_id=db_order.id,
        status=models.OrderStatus.CREATED,
        notes="Order created from offer."
    )
    db.add(db_status_history)

    db.add(db_order)
    await db.commit()

    # Eagerly load relationships for the response
    await db.refresh(db_order, attribute_names=["segments", "status_history"])

    # 5. Publish event to Kafka
    kafka_producer.publish_order_created(
        {
            "orderId": str(db_order.id),
            "clientId": str(db_order.client_id),
            "supplierId": str(db_order.supplier_id),
            "totalPrice": float(db_order.price_amount),
            "currency": db_order.price_currency
        }
    )
    return db_order

async def get_order_by_id(db: AsyncSession, order_id: uuid.UUID):
    result = await db.execute(
        select(models.Order)
        .where(models.Order.id == order_id)
        .options(
            selectinload(models.Order.segments),
            selectinload(models.Order.status_history)
        )
    )
    return result.scalars().first()

async def list_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Order)
        .order_by(models.Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(models.Order.segments),
            selectinload(models.Order.status_history)
        )
    )
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id: uuid.UUID, status_update: schemas.OrderStatusUpdate):
    db_order = await get_order_by_id(db, order_id)
    if not db_order:
        return None

    # Update status and create a history entry
    db_order.status = status_update.status
    db_status_history = models.StatusHistory(
        order_id=db_order.id,
        status=status_update.status,
        notes=status_update.notes
    )
    db.add(db_status_history)

    await db.commit()
    await db.refresh(db_order, attribute_names=["status_history"])

    # Publish events for key status changes
    kafka_producer.publish_order_status_updated(
        {
            "orderId": str(db_order.id),
            "newStatus": db_order.status.value,
        }
    )
    if db_order.status == models.OrderStatus.POD_CONFIRMED:
        kafka_producer.publish_pod_confirmed(
            {
                "orderId": str(db_order.id),
                "confirmedBy": "user_id_placeholder" # This would come from the current user context
            }
        )

    return db_order
