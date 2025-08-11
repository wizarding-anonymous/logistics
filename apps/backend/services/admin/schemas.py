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

class KYCRejectionRequest(BaseModel):
    reason: str
