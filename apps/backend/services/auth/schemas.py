import uuid
import re
from pydantic import BaseModel, EmailStr, validator, constr
from typing import List, Optional

# =================================
# User Schemas
# =================================

class UserBase(BaseModel):
    email: EmailStr
    phone_number: Optional[str] = None
    roles: List[str] = ['client']

    @validator('roles')
    def validate_roles(cls, v):
        allowed_roles = {'client', 'supplier'}
        if not set(v).issubset(allowed_roles):
            raise ValueError(f"Invalid role provided. Allowed roles are: {', '.join(allowed_roles)}")
        return v

    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format (simple E.164-like regex)."""
        if v is None:
            return v
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format. Use E.164 format (e.g., +14155552671).')
        return v

class UserCreate(UserBase):
    password: constr(min_length=8)
    recaptcha_token: str

    @validator('password', pre=True)
    def validate_password_strength(cls, v):
        """
        Validates the password strength.
        - At least one digit.
        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one special character.
        """
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit.')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character.')
        return v

class KYCDocumentBase(BaseModel):
    document_type: str
    file_storage_key: str

class KYCDocumentCreate(KYCDocumentBase):
    pass

class KYCDocument(KYCDocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str # Should match KYCStatus enum
    rejection_reason: Optional[str] = None
    uploaded_at: str

    class Config:
        orm_mode = True

class User(UserBase):
    id: uuid.UUID
    is_active: bool
    kyc_documents: List[KYCDocument] = []

    class Config:
        orm_mode = True

# =================================
# Token Schemas
# =================================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str # 'sub' is the standard claim for subject (user identifier)
    scopes: List[str] = []

# =================================
# TFA Schemas
# =================================

class TFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str

class TFAEnableRequest(BaseModel):
    code: str

class TokenRequestWithTFA(BaseModel):
    username: EmailStr
    password: str
    tfa_code: str
