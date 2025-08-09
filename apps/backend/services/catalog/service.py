import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models, schemas

async def create_service_offering(
    db: AsyncSession,
    service_in: schemas.ServiceOfferingCreate,
    supplier_org_id: uuid.UUID
):
    """
    Creates a new Service Offering and its associated Tariffs.
    """
    # Create the main service offering object
    db_service = models.ServiceOffering(
        supplier_organization_id=supplier_org_id,
        name=service_in.name,
        description=service_in.description,
        service_type=service_in.service_type,
        is_active=service_in.is_active
    )

    # Create the associated tariff objects
    for tariff_in in service_in.tariffs:
        db_tariff = models.Tariff(
            price=tariff_in.price,
            currency=tariff_in.currency,
            unit=tariff_in.unit
        )
        db_service.tariffs.append(db_tariff)

    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service

async def list_service_offerings(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of active service offerings with pagination.
    """
    result = await db.execute(
        select(models.ServiceOffering)
        .where(models.ServiceOffering.is_active == True)
        .options(selectinload(models.ServiceOffering.tariffs))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_service_offering_by_id(db: AsyncSession, service_id: uuid.UUID):
    """
    Retrieves a single service offering by its UUID, including its tariffs.
    """
    result = await db.execute(
        select(models.ServiceOffering)
        .where(models.ServiceOffering.id == service_id)
        .options(selectinload(models.ServiceOffering.tariffs))
    )
    return result.scalars().first()
