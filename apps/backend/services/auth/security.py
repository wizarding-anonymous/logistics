import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# =================================
# Password Hashing
# =================================

# Use bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# =================================
# JSON Web Tokens (JWT)
# =================================

# These should be loaded from environment variables in a real application
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_long_and_random")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# =================================
# Two-Factor Authentication (TFA/TOTP)
# =================================

import pyotp

def generate_tfa_secret() -> str:
    """Generate a new base32 secret for TOTP."""
    return pyotp.random_base32()

def verify_tfa_code(secret: str, code: str) -> bool:
    """Verify a TOTP code against the secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def generate_tfa_provisioning_uri(email: str, secret: str, issuer_name: str = "LogisticsMarketplace") -> str:
    """Generate a provisioning URI for use in authenticator apps."""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)

# =================================
# reCAPTCHA Verification
# =================================

import httpx

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "your_recaptcha_secret_key_here")

async def verify_recaptcha(token: str) -> bool:
    """
    Verifies a reCAPTCHA v2 token with Google's API.
    """
    if not RECAPTCHA_SECRET_KEY or "your_recaptcha_secret_key_here" in RECAPTCHA_SECRET_KEY:
        # Don't run verification if the secret key is not configured.
        # This allows disabling reCAPTCHA in local/test environments.
        print("Warning: RECAPTCHA_SECRET_KEY is not configured. Skipping verification.")
        return True

    async with httpx.AsyncClient() as client:
        response = await client.post(
            RECAPTCHA_VERIFY_URL,
            data={"secret": RECAPTCHA_SECRET_KEY, "response": token},
        )
        response.raise_for_status()
        result = response.json()
        return result.get("success", False)


# =================================
# RBAC (Role-Based Access Control)
# =================================

import yaml
import uuid
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Dict, Set

# Assume the rbac-matrix.yaml is at the root of the monorepo
# Adjust path as necessary if the service runs from a different directory
RBAC_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'rbac-matrix.yaml')


@lru_cache()
def get_rbac_matrix() -> Dict[str, Set[str]]:
    """
    Loads and parses the RBAC YAML file, converting it into a dictionary
    mapping roles to a set of their permissions.
    Using lru_cache makes this a singleton that only runs once.
    """
    try:
        with open(RBAC_FILE_PATH, 'r') as f:
            rbac_data = yaml.safe_load(f)
    except FileNotFoundError:
        # Handle case where file doesn't exist, maybe in a test environment
        return {}

    role_permissions = {}
    permissions_map = {p['id']: p for p in rbac_data.get('permissions', [])}

    for role in rbac_data.get('roles', []):
        role_name = role['name']
        # The 'admin' role gets all permissions implicitly
        if role_name == 'admin':
            role_permissions[role_name] = set(permissions_map.keys())
            continue

        permissions = set(role.get('permissions', []))
        role_permissions[role_name] = permissions

    return role_permissions


class UserContext(BaseModel):
    """Pydantic model to represent the user data extracted from the JWT."""
    id: uuid.UUID
    roles: List[str]
    org_id: Optional[uuid.UUID] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user_context(token: str = Depends(oauth2_scheme)) -> UserContext:
    """
    Generic dependency to decode JWT and return a UserContext.
    This can be shared across services.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
        roles = payload.get("roles", [])
        org_id_str = payload.get("org_id")
        org_id = uuid.UUID(org_id_str) if org_id_str else None
        return UserContext(id=user_id, roles=roles, org_id=org_id)
    except (ValueError, TypeError):
        raise credentials_exception


def require_permission(permission: str):
    """
    This is a dependency factory. It creates a dependency that will
    check if the current user has the required permission.
    """
    def permission_checker(user_context: UserContext = Depends(get_current_user_context)):
        rbac_matrix = get_rbac_matrix()
        user_permissions: Set[str] = set()
        for role in user_context.roles:
            user_permissions.update(rbac_matrix.get(role, set()))

        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required.",
            )
    return permission_checker
