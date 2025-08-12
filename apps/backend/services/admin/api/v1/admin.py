import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service, security
from ...database import get_db

router = APIRouter()

@router.get("/kyc/pending", response_model=List[schemas.UserWithKYC])
async def get_pending_kyc_requests(
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Get a list of all users with pending KYC documents.
    """
    return await service.list_pending_kyc_users(db)

@router.post("/kyc/documents/{doc_id}/approve", response_model=schemas.KYCDocument)
async def approve_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Approve a KYC document.
    """
    approved_doc = await service.approve_kyc_document(db, doc_id)
    if not approved_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return approved_doc

@router.post("/kyc/documents/{doc_id}/reject", response_model=schemas.KYCDocument)
async def reject_document(
    doc_id: uuid.UUID,
    rejection_data: schemas.KYCRejectionRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Reject a KYC document with a reason.
    """
    rejected_doc = await service.reject_kyc_document(db, doc_id, rejection_data.reason)
    if not rejected_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return rejected_doc
