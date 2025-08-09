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

@router.get("/teams/{team_id}", response_model=schemas.Team)
async def get_team_endpoint(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authz check to ensure user is part of the team's organization
):
    """
    Get details for a specific team.
    """
    db_team = await service.get_team(db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.put("/teams/{team_id}", response_model=schemas.Team)
async def update_team_endpoint(
    team_id: uuid.UUID,
    team_in: schemas.TeamUpdate,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authz check
):
    """
    Update a team's details.
    """
    return await service.update_team(db=db, team_id=team_id, team_in=team_in)

@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_endpoint(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authz check
):
    """
    Delete a team.
    """
    await service.delete_team(db=db, team_id=team_id)
    return

@router.post("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_team_member_endpoint(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authz check
):
    """
    Add a user to a team.
    """
    # TODO: Check if user is part of the organization first
    return await service.add_user_to_team(db=db, team_id=team_id, user_id=user_id)

@router.delete("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member_endpoint(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authz check
):
    """
    Remove a user from a team.
    """
    return await service.remove_user_from_team(db=db, team_id=team_id, user_id=user_id)
