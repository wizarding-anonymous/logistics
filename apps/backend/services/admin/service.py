import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models

async def list_pending_kyc_users(db: AsyncSession) -> list[models.User]:
    """
    Lists all users who have at least one KYC document with 'pending' status.
    """
    result = await db.execute(
        select(models.User)
        .join(models.KYCDocument)
        .where(models.KYCDocument.status == models.KYCStatus.PENDING)
        .options(selectinload(models.User.kyc_documents))
        .distinct()
    )
    return result.scalars().all()

async def approve_kyc_document(db: AsyncSession, doc_id: uuid.UUID) -> models.KYCDocument | None:
    """
    Approves a specific KYC document.
    """
    doc = await db.get(models.KYCDocument, doc_id)
    if not doc:
        return None

    doc.status = models.KYCStatus.APPROVED
    doc.rejection_reason = None # Clear any previous rejection reason
    await db.commit()
    await db.refresh(doc)
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

async def reject_kyc_document(db: AsyncSession, doc_id: uuid.UUID, reason: str) -> models.KYCDocument | None:
    """
    Rejects a specific KYC document with a reason.
    """
    doc = await db.get(models.KYCDocument, doc_id)
    if not doc:
        return None

    doc.status = models.KYCStatus.REJECTED
    doc.rejection_reason = reason
    await db.commit()
    await db.refresh(doc)
    return doc
