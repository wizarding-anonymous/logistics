import uuid
from pydantic import BaseModel
from typing import List, Optional

# =================================
# Schemas for API Responses
# =================================

class KYCDocument(BaseModel):
    id: uuid.UUID
    document_type: str
    file_storage_key: str
    status: str
    rejection_reason: Optional[str] = None

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

from datetime import datetime

class UpdateUserRoles(BaseModel):
    roles: List[str]
