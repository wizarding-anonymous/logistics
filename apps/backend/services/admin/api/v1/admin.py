import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ... import schemas, service, security, models
from ...database import get_db

router = APIRouter()

@router.get("/kyc/pending", response_model=List[schemas.UserWithKYC])
async def get_pending_kyc_requests(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Get a list of all users with pending KYC documents.
    """
    return await service.list_pending_kyc_users(db, limit=limit, offset=offset)

@router.get("/kyc/documents", response_model=List[schemas.KYCDocumentWithUser])
async def get_kyc_documents_for_review(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Get KYC documents for admin review with optional status filter.
    Status options: pending, approved, rejected, validation_failed, virus_infected
    """
    return await service.get_kyc_documents_for_review(db, status_filter=status, limit=limit, offset=offset)

@router.get("/kyc/statistics", response_model=dict)
async def get_kyc_statistics(
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Get KYC statistics for admin dashboard.
    """
    return await service.get_kyc_statistics(db)

@router.post("/kyc/documents/{doc_id}/approve", response_model=schemas.KYCDocument)
async def approve_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Approve a KYC document.
    """
    reviewer_id = admin_user.get('user_id') if admin_user else None
    approved_doc = await service.approve_kyc_document(db, doc_id, reviewed_by=reviewer_id)
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
    reviewer_id = admin_user.get('user_id') if admin_user else None
    rejected_doc = await service.reject_kyc_document(db, doc_id, rejection_data.reason, reviewed_by=reviewer_id)
    if not rejected_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return rejected_doc

@router.get("/kyc/documents/{doc_id}/download-url", response_model=dict)
async def get_kyc_document_download_url(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(security.require_admin_role),
):
    """
    Get a presigned URL for downloading a KYC document (admin only).
    """
    doc = await db.get(models.KYCDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Import S3 client from auth service
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'auth'))
    from s3_client import s3_client
    
    download_url = s3_client.generate_presigned_url(
        doc.file_storage_key,
        expiration=3600,  # 1 hour
        http_method='GET'
    )
    
    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )
    
    return {
        "download_url": download_url,
        "file_name": doc.file_name,
        "expires_in": 3600
    }

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
