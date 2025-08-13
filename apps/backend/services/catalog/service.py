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
    offering_data = service_in.dict(exclude={"tariffs"})
    db_service = models.ServiceOffering(
        **offering_data,
        supplier_organization_id=supplier_org_id
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

async def get_tariffs_for_supplier(db: AsyncSession, supplier_org_id: uuid.UUID, service_type: str):
    """
    Retrieves all tariffs for a given supplier and service type.
    This is intended for internal, service-to-service communication.
    """
    result = await db.execute(
        select(models.Tariff)
        .join(models.ServiceOffering)
        .where(
            models.ServiceOffering.supplier_organization_id == supplier_org_id,
            models.ServiceOffering.service_type == service_type,
            models.ServiceOffering.is_active == True
        )
    )
    return result.scalars().all()

from decimal import Decimal

async def update_supplier_ratings(db: AsyncSession, supplier_id: str, new_rating: int):
    """
    Updates the average rating for all service offerings of a supplier.
    """
    # Convert supplier_id string from event to UUID
    supplier_uuid = uuid.UUID(supplier_id)

    # Get all service offerings for the supplier
    result = await db.execute(
        select(models.ServiceOffering).where(models.ServiceOffering.supplier_organization_id == supplier_uuid)
    )
    offerings = result.scalars().all()

    for offering in offerings:
        old_avg = offering.rating_avg or Decimal(0)
        old_count = offering.rating_count or 0

        # Calculate new average
        new_count = old_count + 1
        new_avg = ((old_avg * old_count) + new_rating) / new_count

        offering.rating_avg = new_avg
        offering.rating_count = new_count

    await db.commit()
    return True

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

async def list_service_offerings_by_supplier(db: AsyncSession, supplier_org_id: uuid.UUID):
    """
    Retrieves a list of all service offerings for a specific supplier organization.
    """
    result = await db.execute(
        select(models.ServiceOffering)
        .where(models.ServiceOffering.supplier_organization_id == supplier_org_id)
        .options(selectinload(models.ServiceOffering.tariffs))
        .order_by(models.ServiceOffering.created_at.desc())
    )
    return result.scalars().all()

async def update_service_offering(
    db: AsyncSession,
    service_id: uuid.UUID,
    service_in: schemas.ServiceOfferingUpdate,
    supplier_org_id: uuid.UUID # Added for authorization check
):
    db_service = await get_service_offering_by_id(db, service_id=service_id)
    if not db_service:
        return None

    # Authorization check: Ensure the user's org matches the service's org
    if db_service.supplier_organization_id != supplier_org_id:
        return None # Or raise an exception

    update_data = service_in.dict(exclude_unset=True, exclude={"tariffs"})
    for key, value in update_data.items():
        setattr(db_service, key, value)

    # TODO: Add logic to update/add/remove tariffs

    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service
