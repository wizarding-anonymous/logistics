import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service, security
from ...database import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    return uuid.UUID(user_id_str)

async def get_current_supplier_org_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    """
    Dependency to get the supplier's organization ID from the JWT token.
    This assumes the 'org_id' is a custom claim in the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not a supplier or org_id not in token.",
    )
    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception

    roles = payload.get("roles", [])
    if "supplier" not in roles:
        raise credentials_exception

    org_id_str: str = payload.get("org_id")
    if org_id_str is None:
        raise credentials_exception
    return uuid.UUID(org_id_str)


@router.post("/services", response_model=schemas.ServiceOffering, status_code=status.HTTP_201_CREATED)
async def create_service_offering_endpoint(
    service_in: schemas.ServiceOfferingCreate,
    db: AsyncSession = Depends(get_db),
    supplier_org_id: uuid.UUID = Depends(get_current_supplier_org_id),
):
    return await service.create_service_offering(
        db=db, service_in=service_in, supplier_org_id=supplier_org_id
    )

@router.get("/supplier/services", response_model=List[schemas.ServiceOffering])
async def list_my_services_endpoint(
    db: AsyncSession = Depends(get_db),
    supplier_org_id: uuid.UUID = Depends(get_current_supplier_org_id),
):
    """Lists all service offerings for the authenticated supplier's organization."""
    return await service.list_service_offerings_by_supplier(db=db, supplier_org_id=supplier_org_id)


@router.get("/services", response_model=List[schemas.ServiceOffering])
async def list_public_services_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint to list all active services."""
    return await service.list_service_offerings(db=db, skip=skip, limit=limit)

@router.get("/services/{service_id}", response_model=schemas.ServiceOffering)
async def get_service_endpoint(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    db_service = await service.get_service_offering_by_id(db, service_id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service offering not found")
    return db_service

@router.put("/services/{service_id}", response_model=schemas.ServiceOffering)
async def update_service_offering_endpoint(
    service_id: uuid.UUID,
    service_in: schemas.ServiceOfferingUpdate,
    db: AsyncSession = Depends(get_db),
    supplier_org_id: uuid.UUID = Depends(get_current_supplier_org_id),
):
    updated_service = await service.update_service_offering(
        db=db, service_id=service_id, service_in=service_in, supplier_org_id=supplier_org_id
    )
    if updated_service is None:
        raise HTTPException(status_code=404, detail="Service offering not found or not authorized")
    return updated_service

@router.get("/internal/tariffs", response_model=List[schemas.Tariff])
async def get_tariffs_for_pricing_endpoint(
    supplier_org_id: uuid.UUID,
    service_type: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Internal endpoint for the Pricing service to fetch relevant tariffs.
    NOTE: In a production system, this should be secured (e.g., via network policies
    or a service-to-service auth token) to prevent external access.
    """
    return await service.get_tariffs_for_supplier(
        db=db, supplier_org_id=supplier_org_id, service_type=service_type
    )
