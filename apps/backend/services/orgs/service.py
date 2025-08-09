import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import secrets
from datetime import datetime, timedelta
from sqlalchemy import insert

from . import models, schemas

async def create_organization(db: AsyncSession, org_in: schemas.OrganizationCreate, owner_id: uuid.UUID):
    """
    Creates a new organization and assigns the creating user as its owner.
    This should be an atomic operation.
    """
    # Create the organization instance
    db_org = models.Organization(
        name=org_in.name,
        description=org_in.description
    )
    db.add(db_org)

    # We need to commit here to get the generated org ID for the link table
    # A more robust solution might use SAVEPOINTs or other transaction control,
    # but for this MVP, we commit and then add the owner.
    await db.commit()
    await db.refresh(db_org)

    # Add the owner to the organization
    link_stmt = insert(models.user_organization_link).values(
        user_id=owner_id,
        organization_id=db_org.id,
        role='owner'
    )
    await db.execute(link_stmt)
    await db.commit()

    return db_org

async def get_organization_by_id(db: AsyncSession, org_id: uuid.UUID):
    """
    Retrieves an organization by its UUID.
    """
    result = await db.execute(select(models.Organization).where(models.Organization.id == org_id))
    return result.scalars().first()

async def get_organization_members(db: AsyncSession, org_id: uuid.UUID):
    """
    Retrieves a list of members for a given organization.
    """
    query = select(
        models.user_organization_link.c.user_id,
        models.user_organization_link.c.role
    ).where(models.user_organization_link.c.organization_id == org_id)

    result = await db.execute(query)
    return result.all()

async def create_invitation(db: AsyncSession, org_id: uuid.UUID, invite_in: schemas.InvitationCreate):
    """
    Creates a new invitation for a user to join an organization.
    """
    # Generate a secure, URL-safe token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    new_invitation = models.Invitation(
        token=token,
        organization_id=org_id,
        email=invite_in.email,
        role=invite_in.role,
        status=models.InvitationStatus.PENDING,
        expires_at=expires_at
    )
    db.add(new_invitation)
    await db.commit()
    await db.refresh(new_invitation)

    # In a real app, you would email this token to the user.
    # For now, we just return the invitation object.
    return new_invitation

async def accept_invitation(db: AsyncSession, token: str, user_id: uuid.UUID):
    """
    Allows a user to accept an invitation, adding them to the organization.
    """
    # Find the invitation
    invite_result = await db.execute(
        select(models.Invitation).where(models.Invitation.token == token)
    )
    invitation = invite_result.scalars().first()

    # Validate the invitation
    if not invitation or invitation.status != models.InvitationStatus.PENDING or invitation.expires_at < datetime.utcnow():
        return None # Or raise an exception indicating invalid/expired token

    # Add user to the organization
    link_stmt = insert(models.user_organization_link).values(
        user_id=user_id,
        organization_id=invitation.organization_id,
        role=invitation.role
    )
    await db.execute(link_stmt)

    # Mark invitation as accepted
    invitation.status = models.InvitationStatus.ACCEPTED

    await db.commit()

    return invitation
