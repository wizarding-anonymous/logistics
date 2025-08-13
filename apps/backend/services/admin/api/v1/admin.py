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

@router.get("/users", response_model=List[schemas.User])
async def list_users_endpoint(
    db: AsyncSession = Depends(get_db),
    _ = Depends(security.require_permission("admin:users:read")),
):
    """
    Get a list of all users.
    """
    return await service.list_users(db)

@router.get("/organizations", response_model=List[schemas.Organization])
async def list_organizations_endpoint(
    db: AsyncSession = Depends(get_db),
    _ = Depends(security.require_permission("admin:users:read")),
):
    """
    Get a list of all organizations.
    """
    return await service.list_organizations(db)

@router.patch("/users/{user_id}/deactivate", response_model=schemas.User)
async def deactivate_user_endpoint(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(security.require_permission("admin:users:manage")),
):
    """
    Deactivate a user account.
    """
    user = await service.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}/roles", response_model=schemas.User)
async def update_user_roles_endpoint(
    user_id: uuid.UUID,
    payload: schemas.UpdateUserRoles,
    db: AsyncSession = Depends(get_db),
    _ = Depends(security.require_permission("admin:users:manage")),
):
    """
    Update the roles of a user.
    """
    user = await service.update_user_roles(db, user_id, payload.roles)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
