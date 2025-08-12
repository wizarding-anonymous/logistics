import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

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

@router.post("/", response_model=schemas.RFQ, status_code=status.HTTP_201_CREATED)
async def create_rfq_endpoint(
    rfq_in: schemas.RFQCreate,
    # In a real app, org_id would come from the user's session/token claims
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    # TODO: IMPORTANT - Add authorization check here.
    # The application must verify that the `user_id` from the token
    # is a member of the `org_id` provided in the request.
    # This requires an internal API call to the 'orgs' service.
    return await service.create_rfq(db=db, rfq_in=rfq_in, user_id=user_id, org_id=org_id)

@router.get("/", response_model=list[schemas.RFQ])
async def list_rfqs_for_organization_endpoint(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    # TODO: IMPORTANT - Add authorization check here as well.
    # Verify the user is a member of the organization they are trying to query.
    return await service.get_rfqs_by_org_id(db=db, org_id=org_id)

@router.get("/{rfq_id}", response_model=schemas.RFQ)
async def get_rfq_endpoint(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id), # Ensures user is logged in
):
    db_rfq = await service.get_rfq_by_id(db, rfq_id=rfq_id)
    if db_rfq is None:
        raise HTTPException(status_code=404, detail="RFQ not found")
    # TODO: Add authz check to ensure user is part of the org that owns the RFQ
    return db_rfq

@router.get("/open-rfqs", response_model=list[schemas.RFQ])
async def list_open_rfqs_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(security.require_supplier_role)
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
    payload: dict = Depends(security.require_supplier_role)
):
    """
    Submit an offer for a specific RFQ.
    Accessible only by suppliers. The supplier's org_id is extracted from the token.
    """
    supplier_org_id_str = payload.get("org_id")
    if not supplier_org_id_str:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supplier organization ID not found in token.")

    supplier_org_id = uuid.UUID(supplier_org_id_str)

    db_offer = await service.create_offer(
        db=db, offer_in=offer_in, rfq_id=rfq_id, supplier_org_id=supplier_org_id
    )
    if db_offer is None:
        raise HTTPException(status_code=404, detail="RFQ not found or is not open for offers")
    return db_offer

@router.post("/offers/{offer_id}/accept", response_model=schemas.Offer)
async def accept_offer_endpoint(
    offer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    # TODO: Add authz check to ensure the user accepting is the one who created the RFQ
    accepted_offer = await service.accept_offer(db, offer_id=offer_id)
    if accepted_offer is None:
        raise HTTPException(status_code=404, detail="Offer not found or could not be accepted")
    return accepted_offer
