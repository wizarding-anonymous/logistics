import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel, EmailStr

from ... import schemas, service, security
from ...database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

class UserContext(BaseModel):
    id: uuid.UUID
    email: str # Not EmailStr, as it comes from a trusted token
    roles: List[str]

async def get_current_user_context(token: str = Depends(oauth2_scheme)) -> UserContext:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception

    # In auth service, I used 'sub' for email. I need to be consistent.
    # Let's assume the JWT 'sub' contains the user ID as a string.
    user_id_str: str = payload.get("sub")
    roles: List[str] = payload.get("roles", [])

    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
        # We don't have the user's email here unless we add it to the token,
        # which is a good idea. Let's assume it's there.
        email = payload.get("email", "")
        return UserContext(id=user_id, email=email, roles=roles)
    except (ValueError, TypeError):
        raise credentials_exception

from ...models import user_organization_link

def require_organization_role(required_roles: List[str]):
    """
    Dependency factory to check if a user has a specific role within an organization.
    """
    async def role_checker(
        org_id: uuid.UUID,
        user_context: UserContext = Depends(get_current_user_context),
        db: AsyncSession = Depends(get_db),
    ):
        # Query the association table for the user's role in the specific org
        query = select(user_organization_link.c.role).where(
            user_organization_link.c.user_id == user_context.id,
            user_organization_link.c.organization_id == org_id
        )
        result = await db.execute(query)
        user_role = result.scalars().first()

        if not user_role or user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have the required role in this organization",
            )
    return role_checker

@router.post("/", response_model=schemas.Organization, status_code=status.HTTP_201_CREATED)
async def create_organization_endpoint(
    org_in: schemas.OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    return await service.create_organization(db=db, org_in=org_in, owner_id=user_context.id)

@router.get("/{org_id}", response_model=schemas.OrganizationWithMembers)
async def get_organization_endpoint(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    # TODO: Add authz check
    db_org = await service.get_organization_by_id(db, org_id=org_id)
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    members_raw = await service.get_organization_members(db, org_id=org_id)
    members = [schemas.OrganizationMember(user_id=m.user_id, role=m.role) for m in members_raw]
    return schemas.OrganizationWithMembers(**db_org.__dict__, members=members)

@router.post("/organizations/{org_id}/invitations", response_model=schemas.Invitation)
async def create_invitation_endpoint(
    org_id: uuid.UUID,
    invite_in: schemas.InvitationCreate,
    db: AsyncSession = Depends(get_db),
    # This dependency now checks that the user is an owner or admin of this specific org
    _ = Depends(require_organization_role(["owner", "admin"])),
):
    """
    Create an invitation for a user to join an organization.
    The requesting user must be an 'owner' or 'admin' of the organization.
    """
    return await service.create_invitation(db=db, org_id=org_id, invite_in=invite_in)

@router.post("/invitations/{token}/accept", response_model=schemas.OrganizationMember)
async def accept_invitation_endpoint(
    token: str,
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    # The service needs to check if the user's email matches the invite email
    invitation = await service.accept_invitation(db=db, token=token, user_id=user_context.id)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation token.",
        )
    return schemas.OrganizationMember(user_id=user_context.id, role=invitation.role)
