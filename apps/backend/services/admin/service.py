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
