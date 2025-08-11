import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .database import Base

class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

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

    kyc_documents = relationship("KYCDocument", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    document_type = Column(String, nullable=False) # e.g., 'passport', 'inn', 'ogrn'
    file_storage_key = Column(String, nullable=False) # Key to the file in MinIO/S3
    status = Column(SAEnum(KYCStatus), nullable=False, default=KYCStatus.PENDING)
    rejection_reason = Column(String, nullable=True)

    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="kyc_documents")
