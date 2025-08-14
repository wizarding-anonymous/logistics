import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# =================================
# Schemas for API Responses
# =================================

class KYCDocument(BaseModel):
    id: uuid.UUID
    document_type: str
    file_storage_key: str
    file_name: str
    file_size: int
    file_hash: str
    mime_type: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    virus_scan_status: str = 'pending'
    validation_status: str = 'pending'
    validation_errors: Optional[str] = None
    inn_validation_status: Optional[str] = None
    ogrn_validation_status: Optional[str] = None
    extracted_inn: Optional[str] = None
    extracted_ogrn: Optional[str] = None
    uploaded_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[uuid.UUID] = None

    class Config:
        orm_mode = True

class KYCDocumentWithUser(KYCDocument):
    user: 'User'

    class Config:
        orm_mode = True

class UserWithKYC(BaseModel):
    id: uuid.UUID
    email: str
    roles: List[str]
    kyc_documents: List[KYCDocument] = []

    class Config:
        orm_mode = True

# =================================
# Schemas for API Requests
# =================================

class User(BaseModel):
    id: uuid.UUID
    email: str
    roles: List[str]
    is_active: bool

    class Config:
        orm_mode = True

class Organization(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime

    class Config:
        orm_mode = True

class KYCRejectionRequest(BaseModel):
    reason: str

class UpdateUserRoles(BaseModel):
    roles: List[str]
