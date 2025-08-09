import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

# Association Table for the many-to-many relationship between Users and Organizations
user_organization_link = Table('user_organization_link', Base.metadata,
    Column('user_id', UUID(as_uuid=True), primary_key=True),
    Column('organization_id', UUID(as_uuid=True), ForeignKey('organizations.id'), primary_key=True),
    Column('role', String, nullable=False, default='member') # e.g., 'owner', 'admin', 'member'
)

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # The 'members' relationship will be loaded via the association table
    # This setup is conceptual for the service. A direct user model isn't here.
    # We will query the link table directly in the service logic.

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"

import enum

class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, nullable=False, unique=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False, default='member')
    status = Column(String, nullable=False, default=InvitationStatus.PENDING)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)

    organization = relationship("Organization")
