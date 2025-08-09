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

# =================================
# Team Service Functions
# =================================

async def create_team_for_organization(db: AsyncSession, org_id: uuid.UUID, team_in: schemas.TeamCreate):
    db_team = models.Team(**team_in.dict(), organization_id=org_id)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team

async def get_team(db: AsyncSession, team_id: uuid.UUID):
    return await db.get(models.Team, team_id)

async def get_teams_by_organization(db: AsyncSession, org_id: uuid.UUID):
    result = await db.execute(select(models.Team).where(models.Team.organization_id == org_id))
    return result.scalars().all()

async def update_team(db: AsyncSession, team_id: uuid.UUID, team_in: schemas.TeamUpdate):
    db_team = await get_team(db, team_id)
    if db_team:
        update_data = team_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_team, key, value)
        await db.commit()
        await db.refresh(db_team)
    return db_team

async def delete_team(db: AsyncSession, team_id: uuid.UUID):
    db_team = await get_team(db, team_id)
    if db_team:
        await db.delete(db_team)
        await db.commit()
    return db_team

async def add_user_to_team(db: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID):
    stmt = insert(models.user_team_link).values(user_id=user_id, team_id=team_id)
    await db.execute(stmt)
    await db.commit()
    # We might want to return something more meaningful here
    return {"status": "ok"}

async def remove_user_from_team(db: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID):
    stmt = models.user_team_link.delete().where(
        models.user_team_link.c.user_id == user_id,
        models.user_team_link.c.team_id == team_id
    )
    await db.execute(stmt)
    await db.commit()
    return {"status": "ok"}

async def update_organization_member_role(db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, new_role: str):
    stmt = models.user_organization_link.update().where(
        models.user_organization_link.c.organization_id == org_id,
        models.user_organization_link.c.user_id == user_id
    ).values(role=new_role)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

async def remove_organization_member(db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID):
    stmt = models.user_organization_link.delete().where(
        models.user_organization_link.c.organization_id == org_id,
        models.user_organization_link.c.user_id == user_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


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
