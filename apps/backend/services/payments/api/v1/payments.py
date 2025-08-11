import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ... import schemas, models, service
from ...database import get_db
from ...security import get_current_user_context

router = APIRouter()

@router.get("/invoices", response_model=list[schemas.Invoice])
async def list_my_invoices(
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    """
    List all invoices for the user's organization.
    """
    org_id = user_context["org_id"]
    return await service.get_invoices_by_organization(db, org_id=org_id)

@router.post("/invoices/{invoice_id}/pay", response_model=schemas.Invoice)
async def pay_invoice(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_context: dict = Depends(security.get_current_user_context),
):
    """
    Simulates paying an invoice. Updates its status to 'paid'.
    """
    org_id = user_context["org_id"]
    updated_invoice = await service.mark_invoice_as_paid(db, invoice_id=invoice_id, org_id=org_id)

    if updated_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if updated_invoice == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to pay this invoice")

    return updated_invoice

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
