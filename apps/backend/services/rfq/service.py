import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update

from . import models, schemas, kafka_producer

async def create_rfq(db: AsyncSession, rfq_in: schemas.RFQCreate, user_id: uuid.UUID, org_id: uuid.UUID):
    """
    Creates a new RFQ with its nested Cargo and ShipmentSegment details.
    """
    rfq_data = rfq_in.dict(exclude={'cargo', 'segments'})
    db_rfq = models.RFQ(
        **rfq_data,
        user_id=user_id,
        organization_id=org_id
    )

    # Create and associate the Cargo object
    cargo_data = rfq_in.cargo.dict()
    db_cargo = models.Cargo(**cargo_data)
    db_rfq.cargo = db_cargo

    # Create and associate the ShipmentSegment objects
    for i, segment_in in enumerate(rfq_in.segments):
        segment_data = segment_in.dict()
        db_segment = models.ShipmentSegment(**segment_data, sequence=i + 1)
        db_rfq.segments.append(db_segment)

    db.add(db_rfq)
    await db.commit()
    await db.refresh(db_rfq)
    return db_rfq

async def get_rfq_by_id(db: AsyncSession, rfq_id: uuid.UUID):
    result = await db.execute(
        select(models.RFQ)
        .where(models.RFQ.id == rfq_id)
        .options(
            selectinload(models.RFQ.offers),
            selectinload(models.RFQ.cargo),
            selectinload(models.RFQ.segments)
        )
    )
    return result.scalars().first()

async def get_rfqs_by_org_id(db: AsyncSession, org_id: uuid.UUID):
    result = await db.execute(
        select(models.RFQ)
        .where(models.RFQ.organization_id == org_id)
        .options(
            selectinload(models.RFQ.offers),
            selectinload(models.RFQ.cargo),
            selectinload(models.RFQ.segments)
        )
        .order_by(models.RFQ.created_at.desc())
    )
    return result.scalars().all()

async def list_open_rfqs(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of all RFQs that are currently in 'open' status.
    """
    result = await db.execute(
        select(models.RFQ)
        .where(models.RFQ.status == models.RFQStatus.OPEN)
        .options(
            selectinload(models.RFQ.cargo),
            selectinload(models.RFQ.segments)
        )
        .order_by(models.RFQ.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_offer(db: AsyncSession, offer_in: schemas.OfferCreate, rfq_id: uuid.UUID, supplier_org_id: uuid.UUID):
    rfq = await get_rfq_by_id(db, rfq_id)
    if not rfq or rfq.status != models.RFQStatus.OPEN:
        return None

    db_offer = models.Offer(
        **offer_in.dict(),
        rfq_id=rfq_id,
        supplier_organization_id=supplier_org_id
    )
    db.add(db_offer)
    await db.commit()
    await db.refresh(db_offer)
    return db_offer

async def accept_offer(db: AsyncSession, offer_id: uuid.UUID):
    offer_result = await db.execute(
        select(models.Offer)
        .options(selectinload(models.Offer.rfq)) # Eager load the RFQ
        .where(models.Offer.id == offer_id)
    )
    offer_to_accept = offer_result.scalars().first()

    if not offer_to_accept or offer_to_accept.status != models.OfferStatus.PENDING:
        return None

    offer_to_accept.status = models.OfferStatus.ACCEPTED

    rfq = offer_to_accept.rfq
    rfq.status = models.RFQStatus.CLOSED

    await db.execute(
        update(models.Offer)
        .where(models.Offer.rfq_id == rfq.id, models.Offer.id != offer_id)
        .values(status=models.OfferStatus.REJECTED)
    )

    await db.commit()
    await db.refresh(offer_to_accept)
    await db.refresh(rfq)

    # Publish the event to Kafka
    event_payload = {
        "offer_id": str(offer_to_accept.id),
        "rfq_id": str(rfq.id),
        "client_organization_id": str(rfq.organization_id),
        "supplier_organization_id": str(offer_to_accept.supplier_organization_id),
        "price_amount": float(offer_to_accept.price_amount),
        "price_currency": offer_to_accept.price_currency
    }
    kafka_producer.publish_offer_accepted(event_payload)

    return offer_to_accept
