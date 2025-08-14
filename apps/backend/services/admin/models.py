import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Boolean, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, declarative_base

# Using a new Base for this service's ORM mapping, but it refers to the same tables.
Base = declarative_base()

class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    # Define columns needed by the admin service to read and write data
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    roles = Column(ARRAY(String), nullable=False, default=['client'])
    is_active = Column(Boolean, default=True)
    kyc_documents = relationship("KYCDocument", back_populates="user")

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False)
    file_storage_key = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    status = Column(SAEnum(KYCStatus), nullable=False, default=KYCStatus.PENDING)
    rejection_reason = Column(String, nullable=True)
    virus_scan_status = Column(String, default='pending')
    validation_status = Column(String, default='pending')
    validation_errors = Column(String, nullable=True)
    inn_validation_status = Column(String, nullable=True)
    ogrn_validation_status = Column(String, nullable=True)
    extracted_inn = Column(String, nullable=True)
    extracted_ogrn = Column(String, nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    user = relationship("User", back_populates="kyc_documents")

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
