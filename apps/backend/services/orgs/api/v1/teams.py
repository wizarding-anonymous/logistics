import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, service, models
from ...database import get_db
from .orgs import get_current_user_context, require_organization_role # Re-use dependency

router = APIRouter()

# Dependency to check if the user is a member of the organization
def require_org_member():
    return require_organization_role(["owner", "admin", "member"])

# Dependency to check if the user is an admin or owner of the organization
def require_org_admin():
    return require_organization_role(["owner", "admin"])

@router.post("/organizations/{org_id}/teams", response_model=schemas.Team, status_code=status.HTTP_201_CREATED)
async def create_team_endpoint(
    org_id: uuid.UUID,
    team_in: schemas.TeamCreate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_admin()),
):
    """
    Create a new team within an organization. Must be an org admin or owner.
    """
    return await service.create_team_for_organization(db=db, org_id=org_id, team_in=team_in)

@router.get("/organizations/{org_id}/teams", response_model=List[schemas.Team])
async def list_teams_in_organization_endpoint(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_member()),
):
    """
    List all teams within an organization. Must be an org member.
    """
    return await service.get_teams_by_organization(db=db, org_id=org_id)

async def get_team_and_verify_access(
    team_id: uuid.UUID,
    user_context: dict = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
    required_roles: List[str] = ["owner", "admin", "member"],
) -> models.Team:
    """Dependency that gets a team and verifies the user has access to its organization."""
    db_team = await service.get_team(db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    # Now, check if the user is part of the organization that owns the team
    org_id = db_team.organization_id
    role_checker = require_organization_role(required_roles)
    await role_checker(org_id=org_id, user_context=user_context, db=db)

    return db_team

@router.get("/teams/{team_id}", response_model=schemas.Team)
async def get_team_endpoint(
    db_team: models.Team = Depends(get_team_and_verify_access)
):
    """Get details for a specific team. User must be a member of the parent org."""
    return db_team

@router.put("/teams/{team_id}", response_model=schemas.Team)
async def update_team_endpoint(
    team_in: schemas.TeamUpdate,
    db_team: models.Team = Depends(lambda team_id, db, user_context: get_team_and_verify_access(team_id, user_context, db, required_roles=["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Update a team's details. Must be an org admin or owner."""
    return await service.update_team(db=db, team_id=db_team.id, team_in=team_in)

@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_endpoint(
    db_team: models.Team = Depends(lambda team_id, db, user_context: get_team_and_verify_access(team_id, user_context, db, required_roles=["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Delete a team. Must be an org admin or owner."""
    await service.delete_team(db=db, team_id=db_team.id)
    return

@router.post("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_team_member_endpoint(
    user_id: uuid.UUID,
    db_team: models.Team = Depends(lambda team_id, db, user_context: get_team_and_verify_access(team_id, user_context, db, required_roles=["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Add a user to a team. Must be an org admin or owner."""
    # TODO: Check if user_id being added is part of the organization first.
    # This would require another service call or DB query.
    return await service.add_user_to_team(db=db, team_id=db_team.id, user_id=user_id)

@router.delete("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member_endpoint(
    user_id: uuid.UUID,
    db_team: models.Team = Depends(lambda team_id, db, user_context: get_team_and_verify_access(team_id, user_context, db, required_roles=["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user from a team. Must be an org admin or owner."""
    return await service.remove_user_from_team(db=db, team_id=db_team.id, user_id=user_id)
