import uuid
from pydantic import BaseModel, EmailStr
from typing import List, Optional

# =================================
# User Schemas
# =================================

class UserBase(BaseModel):
    email: EmailStr
    roles: List[str] = ['client']

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: uuid.UUID
    is_active: bool

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
