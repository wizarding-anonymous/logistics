import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # The entity this document is associated with (e.g., an order, a user KYC)
    related_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    related_entity_type = Column(String, nullable=False, index=True) # e.g. "order", "kyc"

    document_type = Column(String, nullable=False) # e.g. "pod", "invoice", "cmr"
    filename = Column(String, nullable=False)
    s3_path = Column(String, nullable=False, unique=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Document(filename='{self.filename}', type='{self.document_type}')>"
