import uuid
from sqlalchemy import Column, String, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    # Two-Factor Authentication fields
    tfa_secret = Column(String, nullable=True)
    is_tfa_enabled = Column(Boolean, default=False, nullable=False)

    # Storing roles as an array of strings. Corresponds to roles in rbac-matrix.yaml
    roles = Column(ARRAY(String), nullable=False, default=['client'])

    # For session invalidation
    tokens_revoked_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
