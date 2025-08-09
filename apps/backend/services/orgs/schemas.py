import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# =================================
# Organization Schemas
# =================================

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: uuid.UUID
    subscription_plan_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# =================================
# Team Schemas
# =================================

class TeamBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class Team(TeamBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        orm_mode = True

# =================================
# Membership Schemas
# =================================

class OrganizationMember(BaseModel):
    user_id: uuid.UUID
    role: str # e.g., 'owner', 'admin', 'member'

class UpdateMemberRole(BaseModel):
    role: str

class OrganizationWithMembers(Organization):
    members: List[OrganizationMember]

# =================================
# Invitation Schemas
# =================================

class InvitationCreate(BaseModel):
    email: str = Field(..., description="The email of the user to invite.")
    role: str = Field(default='member', description="The role to grant the user.")

class Invitation(BaseModel):
    id: uuid.UUID
    token: str
    organization_id: uuid.UUID
    email: str
    role: str
    status: str
    expires_at: datetime

    class Config:
        orm_mode = True
