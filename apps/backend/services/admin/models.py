import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Boolean, Enum as SAEnum, ForeignKey
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
    # Define only the columns needed by the admin service to read data
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    roles = Column(ARRAY(String), nullable=False, default=['client'])
    kyc_documents = relationship("KYCDocument", back_populates="user")

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False)
    file_storage_key = Column(String, nullable=False)
    status = Column(SAEnum(KYCStatus), nullable=False, default=KYCStatus.PENDING)
    rejection_reason = Column(String, nullable=True)
    user = relationship("User", back_populates="kyc_documents")
