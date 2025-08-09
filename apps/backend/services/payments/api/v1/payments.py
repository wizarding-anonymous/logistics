import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ... import schemas, models, security
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

@router.get("/invoices/by-order/{order_id}", response_model=schemas.Invoice)
async def get_invoice_for_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Get the invoice and its transactions for a specific order.
    """
    result = await db.execute(
        select(models.Invoice)
        .where(models.Invoice.order_id == order_id)
        .options(selectinload(models.Invoice.transactions))
    )
    invoice = result.scalars().first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found for this order")

    # TODO: Add authorization check to ensure user belongs to the org
    # that owns the invoice.

    return invoice

@router.get("/invoices/by-organization/{org_id}", response_model=list[schemas.Invoice])
async def list_invoices_for_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    List all invoices for a given organization.
    """
    # TODO: Add authz check
    return await service.get_invoices_by_organization(db, org_id=org_id)

@router.get("/payouts/by-organization/{org_id}", response_model=list[schemas.Payout])
async def list_payouts_for_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    List all payouts for a given supplier organization.
    """
    # TODO: Add authz check
    return await service.get_payouts_by_organization(db, org_id=org_id)
