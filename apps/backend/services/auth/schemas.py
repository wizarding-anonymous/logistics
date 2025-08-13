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
    password: constr(min_length=12)
    recaptcha_token: str

    @validator('password', pre=True)
    def validate_password_strength(cls, v):
        """Validate password against security policy"""
        from .security import validate_password_strength
        
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
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
    is_verified: bool
    failed_login_attempts: int
    locked_until: Optional[str] = None
    is_tfa_enabled: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: str
    language: str
    last_login_at: Optional[str] = None
    created_at: str
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
    backup_codes: List[str]

class TFAEnableRequest(BaseModel):
    code: str

class TokenRequestWithTFA(BaseModel):
    username: EmailStr
    password: str
    tfa_code: Optional[str] = None
    backup_code: Optional[str] = None

    @validator('tfa_code', 'backup_code')
    def validate_auth_method(cls, v, values):
        """Ensure either TFA code or backup code is provided"""
        tfa_code = values.get('tfa_code')
        backup_code = values.get('backup_code')
        
        if not tfa_code and not backup_code:
            raise ValueError('Either tfa_code or backup_code must be provided')
        
        if tfa_code and backup_code:
            raise ValueError('Provide either tfa_code or backup_code, not both')
        
        return v

# =================================
# Session Schemas
# =================================

class UserSessionBase(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserSession(UserSessionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: str
    expires_at: str
    last_activity: str
    is_active: bool

    class Config:
        orm_mode = True

class SessionListResponse(BaseModel):
    sessions: List[UserSession]
    total_count: int
    active_count: int

# =================================
# Password Change Schemas
# =================================

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: constr(min_length=12)

    @validator('new_password')
    def validate_new_password_strength(cls, v):
        """Validate new password against security policy"""
        from .security import validate_password_strength
        
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v

class PasswordResetRequest(BaseModel):
    email: EmailStr
    recaptcha_token: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: constr(min_length=12)

    @validator('new_password')
    def validate_new_password_strength(cls, v):
        """Validate new password against security policy"""
        from .security import validate_password_strength
        
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v

# =================================
# Audit Log Schemas
# =================================

class AuditLogBase(BaseModel):
    event_type: str
    event_description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    severity: str = "info"

class AuditLog(AuditLogBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    request_id: Optional[str] = None
    metadata: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True

class AuditLogListResponse(BaseModel):
    logs: List[AuditLog]
    total_count: int

class SecuritySummaryResponse(BaseModel):
    period_hours: int
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
