import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models

async def list_pending_kyc_users(db: AsyncSession, limit: int = 50, offset: int = 0) -> list[models.User]:
    """
    Lists all users who have at least one KYC document with 'pending' status.
    """
    result = await db.execute(
        select(models.User)
        .join(models.KYCDocument)
        .where(models.KYCDocument.status == models.KYCStatus.PENDING)
        .options(selectinload(models.User.kyc_documents))
        .distinct()
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

async def get_kyc_documents_for_review(db: AsyncSession, status_filter: str = None, limit: int = 50, offset: int = 0):
    """
    Get KYC documents for admin review with optional status filter
    """
    query = select(models.KYCDocument).options(selectinload(models.KYCDocument.user))
    
    if status_filter:
        if status_filter == 'pending':
            query = query.where(models.KYCDocument.status == models.KYCStatus.PENDING)
        elif status_filter == 'approved':
            query = query.where(models.KYCDocument.status == models.KYCStatus.APPROVED)
        elif status_filter == 'rejected':
            query = query.where(models.KYCDocument.status == models.KYCStatus.REJECTED)
        elif status_filter == 'validation_failed':
            query = query.where(models.KYCDocument.validation_status == 'invalid')
        elif status_filter == 'virus_infected':
            query = query.where(models.KYCDocument.virus_scan_status == 'infected')
    
    query = query.order_by(models.KYCDocument.uploaded_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_kyc_statistics(db: AsyncSession):
    """
    Get KYC statistics for admin dashboard
    """
    from sqlalchemy import func, case
    
    # Count documents by status
    status_counts = await db.execute(
        select(
            models.KYCDocument.status,
            func.count(models.KYCDocument.id).label('count')
        ).group_by(models.KYCDocument.status)
    )
    
    status_stats = {row.status: row.count for row in status_counts}
    
    # Count users by KYC completion status
    user_stats = await db.execute(
        select(
            func.count(models.User.id).label('total_users'),
            func.count(case((models.KYCDocument.status == models.KYCStatus.APPROVED, 1))).label('verified_users'),
            func.count(case((models.KYCDocument.status == models.KYCStatus.PENDING, 1))).label('pending_users'),
            func.count(case((models.KYCDocument.status == models.KYCStatus.REJECTED, 1))).label('rejected_users')
        ).select_from(models.User).outerjoin(models.KYCDocument)
    )
    
    user_row = user_stats.first()
    
    return {
        'document_status': status_stats,
        'user_stats': {
            'total_users': user_row.total_users,
            'verified_users': user_row.verified_users,
            'pending_users': user_row.pending_users,
            'rejected_users': user_row.rejected_users
        }
    }

async def approve_kyc_document(db: AsyncSession, doc_id: uuid.UUID, reviewed_by: uuid.UUID = None) -> models.KYCDocument | None:
    """
    Approves a specific KYC document.
    """
    from sqlalchemy.orm import selectinload
    
    # Get document with user info for notifications
    result = await db.execute(
        select(models.KYCDocument)
        .options(selectinload(models.KYCDocument.user))
        .where(models.KYCDocument.id == doc_id)
    )
    doc = result.scalars().first()
    
    if not doc:
        return None

    doc.status = models.KYCStatus.APPROVED
    doc.rejection_reason = None # Clear any previous rejection reason
    doc.reviewed_at = func.now()
    doc.reviewed_by = reviewed_by
    
    await db.commit()
    await db.refresh(doc)
    
    # Send notification (async)
    if doc.user and doc.user.email:
        import asyncio
        from ..auth.kyc_notifications import kyc_notification_service
        
        asyncio.create_task(
            kyc_notification_service.send_document_approved_notification(
                doc.user.email, doc.document_type
            )
        )
    
    return doc

async def list_users(db: AsyncSession):
    """
    Returns a list of all users.
    """
    result = await db.execute(select(models.User).order_by(models.User.email))
    return result.scalars().all()

async def list_organizations(db: AsyncSession):
    """
    Returns a list of all organizations.
    """
    result = await db.execute(select(models.Organization).order_by(models.Organization.name))
    return result.scalars().all()

async def deactivate_user(db: AsyncSession, user_id: uuid.UUID) -> models.User | None:
    """
    Deactivates a user by setting is_active to False.
    """
    user = await db.get(models.User, user_id)
    if not user:
        return None
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_roles(db: AsyncSession, user_id: uuid.UUID, roles: List[str]) -> models.User | None:
    """
    Updates the roles for a specific user.
    """
    user = await db.get(models.User, user_id)
    if not user:
        return None
    user.roles = roles
    await db.commit()
    await db.refresh(user)
    return user

async def reject_kyc_document(db: AsyncSession, doc_id: uuid.UUID, reason: str, reviewed_by: uuid.UUID = None) -> models.KYCDocument | None:
    """
    Rejects a specific KYC document with a reason.
    """
    from sqlalchemy.orm import selectinload
    
    # Get document with user info for notifications
    result = await db.execute(
        select(models.KYCDocument)
        .options(selectinload(models.KYCDocument.user))
        .where(models.KYCDocument.id == doc_id)
    )
    doc = result.scalars().first()
    
    if not doc:
        return None

    doc.status = models.KYCStatus.REJECTED
    doc.rejection_reason = reason
    doc.reviewed_at = func.now()
    doc.reviewed_by = reviewed_by
    
    await db.commit()
    await db.refresh(doc)
    
    # Send notification (async)
    if doc.user and doc.user.email:
        import asyncio
        from ..auth.kyc_notifications import kyc_notification_service
        
        asyncio.create_task(
            kyc_notification_service.send_document_rejected_notification(
                doc.user.email, doc.document_type, reason
            )
        )
    
    return doc
