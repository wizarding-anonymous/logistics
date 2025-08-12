import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models, schemas, kafka_producer

async def create_order(db: AsyncSession, order_in: schemas.OrderCreate):
    """
    Creates a new Order based on the data from an `offer_accepted` event.
    """
    db_order = models.Order(
        client_id=order_in.client_id,
        supplier_id=order_in.supplier_id,
        price_amount=order_in.price_amount,
        price_currency=order_in.price_currency,
        status=models.OrderStatus.CREATED
    )
    db.add(db_order)

    # It's better to commit here to get the order ID before creating children,
    # or configure the session to do this automatically.
    # For now, we assume the relationship handles this.

    # Create the initial StatusHistory entry
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

async def update_order_status(
    db: AsyncSession,
    order_id: uuid.UUID,
    status_update: schemas.OrderStatusUpdate,
    user_context: dict,
):
    db_order = await get_order_by_id(db, order_id)
    if not db_order:
        return None

    # Authorization Check: Only the assigned supplier can update the status
    if db_order.supplier_id != user_context["org_id"]:
        return "unauthorized" # Special return value to indicate auth failure

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
    # If the order is now complete, publish an event for the billing service
    if db_order.status == models.OrderStatus.POD_CONFIRMED:
        kafka_producer.publish_order_completed(
            {
                "orderId": str(db_order.id),
                "clientId": str(db_order.client_id),
                "supplierId": str(db_order.supplier_id),
                "totalPrice": float(db_order.price_amount),
                "currency": db_order.price_currency,
                "confirmedAt": db_order.updated_at.isoformat(),
            }
        )

    return db_order

async def create_review_for_order(db: AsyncSession, order_id: uuid.UUID, review_in: schemas.ReviewCreate, user_context: dict):
    """
    Creates a review for a completed order.
    """
    order = await get_order_by_id(db, order_id=order_id)
    if not order:
        return None # Not found

    # Authz check: Only the client who created the order can review it.
    if order.client_id != user_context["org_id"]:
        return "unauthorized"

    # Business logic check: Can only review a completed order
    if order.status != models.OrderStatus.CLOSED and order.status != models.OrderStatus.POD_CONFIRMED:
        return "not_completed"

    # Business logic check: Can only review once
    if order.review:
        return "already_reviewed"

    db_review = models.Review(
        order_id=order_id,
        reviewer_id=user_context["user_id"],
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    # TODO: In a real app, publish a "review_created" event here
    # so the catalog service can update the supplier's average rating.

    return db_review
