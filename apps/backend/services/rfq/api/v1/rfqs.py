import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ... import schemas, service, security
from ...database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.RFQ, status_code=status.HTTP_201_CREATED)
async def create_rfq_endpoint(
    rfq_in: schemas.RFQCreate,
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.get_current_user_context),
    _ = Depends(security.require_permission("rfq:create")),
):
    if not user_context.org_id:
        raise HTTPException(status_code=403, detail="User must belong to an organization to create an RFQ.")

    return await service.create_rfq(db=db, rfq_in=rfq_in, user_id=user_context.id, org_id=user_context.org_id)

@router.get("/", response_model=list[schemas.RFQ])
async def list_rfqs_for_organization_endpoint(
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.get_current_user_context),
    _ = Depends(security.require_permission("rfq:read:own")),
):
    if not user_context.org_id:
        raise HTTPException(status_code=403, detail="User is not associated with an organization.")
    return await service.get_rfqs_by_org_id(db=db, org_id=user_context.org_id)

@router.get("/{rfq_id}", response_model=schemas.RFQ)
async def get_rfq_endpoint(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.get_current_user_context),
):
    db_rfq = await service.get_rfq_by_id(db, rfq_id=rfq_id)
    if db_rfq is None:
        raise HTTPException(status_code=404, detail="RFQ not found")

    # Authz check: User must be from the org that owns the RFQ, or be a supplier.
    if "supplier" not in user_context.roles and db_rfq.organization_id != user_context.org_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this RFQ.")
    return db_rfq

@router.get("/open-rfqs/", response_model=list[schemas.RFQ])
async def list_open_rfqs_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _ = Depends(security.require_supplier_role)
):
    """
    Lists all RFQs that are currently open for bidding.
    Accessible only by users with the 'supplier' role.
    """
    return await service.list_open_rfqs(db=db, skip=skip, limit=limit)

@router.post("/{rfq_id}/offers", response_model=schemas.Offer)
async def create_offer_endpoint(
    rfq_id: uuid.UUID,
    offer_in: schemas.OfferCreate,
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.require_supplier_role)
):
    """
    Submit an offer for a specific RFQ.
    Accessible only by suppliers. The supplier's org_id is extracted from the token.
    """
    if not user_context.org_id:
        raise HTTPException(status_code=403, detail="Supplier organization ID not found in token.")

    db_offer = await service.create_offer(
        db=db, offer_in=offer_in, rfq_id=rfq_id, supplier_org_id=user_context.org_id
    )
    if db_offer is None:
        raise HTTPException(status_code=404, detail="RFQ not found or is not open for offers")
    return db_offer

@router.post("/offers/{offer_id}/accept", response_model=schemas.Offer)
async def accept_offer_endpoint(
    offer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_context: security.UserContext = Depends(security.get_current_user_context),
    _ = Depends(security.require_permission("rfq:create")) # Only a client can accept
):
    accepted_offer = await service.accept_offer(db, offer_id=offer_id, user_org_id=user_context.org_id)
    if accepted_offer is None:
        raise HTTPException(status_code=404, detail="Offer not found or could not be accepted")
    if accepted_offer == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to accept this offer")
    return accepted_offer
