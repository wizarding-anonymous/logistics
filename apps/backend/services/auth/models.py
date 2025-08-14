import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Boolean, Enum as SAEnum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY, INET
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
    is_verified = Column(Boolean, default=False)

    # Enhanced security fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)

    # Two-Factor Authentication fields
    tfa_secret = Column(String, nullable=True)
    is_tfa_enabled = Column(Boolean, default=False, nullable=False)
    backup_codes = Column(ARRAY(String), nullable=True)

    # Storing roles as an array of strings. Corresponds to roles in rbac-matrix.yaml
    roles = Column(ARRAY(String), nullable=False, default=['client'])

    # Profile fields
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    timezone = Column(String, default='UTC')
    language = Column(String, default='ru')

    # For session invalidation
    tokens_revoked_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    kyc_documents = relationship("KYCDocument", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    document_type = Column(String, nullable=False) # e.g., 'passport', 'inn', 'ogrn'
    file_storage_key = Column(String, nullable=False) # Key to the file in MinIO/S3
    file_name = Column(String, nullable=False) # Original filename
    file_size = Column(Integer, nullable=False) # File size in bytes
    file_hash = Column(String, nullable=False) # SHA256 hash for integrity
    mime_type = Column(String, nullable=True) # MIME type of the file
    
    status = Column(SAEnum(KYCStatus), nullable=False, default=KYCStatus.PENDING)
    rejection_reason = Column(String, nullable=True)
    
    # Validation results
    virus_scan_status = Column(String, default='pending') # 'pending', 'clean', 'infected'
    validation_status = Column(String, default='pending') # 'pending', 'valid', 'invalid'
    validation_errors = Column(Text, nullable=True) # JSON string of validation errors
    
    # INN/OGRN specific validation
    inn_validation_status = Column(String, nullable=True) # 'valid', 'invalid', 'not_found'
    ogrn_validation_status = Column(String, nullable=True) # 'valid', 'invalid', 'not_found'
    extracted_inn = Column(String, nullable=True) # Extracted INN from document
    extracted_ogrn = Column(String, nullable=True) # Extracted OGRN from document

    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True) # Admin user who reviewed

    user = relationship("User", back_populates="kyc_documents")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="sessions")


class RateLimit(Base):
    __tablename__ = "rate_limits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String(255), nullable=False, index=True)  # IP or user_id
    endpoint = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0)
    window_start = Column(DateTime, server_default=func.now(), nullable=False)
    blocked_until = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_description = Column(Text, nullable=False)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    severity = Column(String(20), default='info')  # info, warning, error, critical
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs")
