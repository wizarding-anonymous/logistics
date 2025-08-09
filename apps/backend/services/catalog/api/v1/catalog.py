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

@router.post("/services", response_model=schemas.ServiceOffering, status_code=status.HTTP_201_CREATED)
async def create_service_offering_endpoint(
    service_in: schemas.ServiceOfferingCreate,
    # In a real app, supplier_org_id would come from the user's session/token
    supplier_org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id), # Ensures user is logged in
):
    # TODO: Add authz check to ensure user is a supplier and belongs to the supplier_org_id
    return await service.create_service_offering(
        db=db, service_in=service_in, supplier_org_id=supplier_org_id
    )

@router.get("/services", response_model=List[schemas.ServiceOffering])
async def list_services_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id), # Ensures user is logged in
):
    return await service.list_service_offerings(db=db, skip=skip, limit=limit)

@router.get("/services/{service_id}", response_model=schemas.ServiceOffering)
async def get_service_endpoint(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id), # Ensures user is logged in
):
    db_service = await service.get_service_offering_by_id(db, service_id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service offering not found")
    return db_service
