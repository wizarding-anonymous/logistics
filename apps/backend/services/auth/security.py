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
# Password Policy Validation
# =================================

import re
import secrets
import string
from typing import List, Tuple

class PasswordPolicy:
    """Password policy validation"""
    
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*(),.?\":{}|<>"
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against policy
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")
        
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if cls.REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if cls.REQUIRE_SPECIAL and not re.search(f'[{re.escape(cls.SPECIAL_CHARS)}]', password):
            errors.append(f"Password must contain at least one special character: {cls.SPECIAL_CHARS}")
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            errors.append("Password cannot contain more than 2 consecutive identical characters")
        
        # Check for sequential characters
        if cls._has_sequential_chars(password):
            errors.append("Password cannot contain sequential characters (e.g., 123, abc)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _has_sequential_chars(password: str, min_length: int = 3) -> bool:
        """Check for sequential characters"""
        password_lower = password.lower()
        
        for i in range(len(password_lower) - min_length + 1):
            substring = password_lower[i:i + min_length]
            
            # Check for sequential letters
            if all(ord(substring[j]) == ord(substring[0]) + j for j in range(len(substring))):
                return True
            
            # Check for sequential digits
            if substring.isdigit():
                if all(int(substring[j]) == int(substring[0]) + j for j in range(len(substring))):
                    return True
        
        return False

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password strength using policy"""
    return PasswordPolicy.validate_password(password)

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

def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA recovery"""
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # Format as XXXX-XXXX for readability
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes

def verify_backup_code(stored_codes: List[str], provided_code: str) -> Tuple[bool, List[str]]:
    """
    Verify backup code and return updated list (with used code removed)
    Returns: (is_valid, remaining_codes)
    """
    if not stored_codes or not provided_code:
        return False, stored_codes
    
    # Normalize the provided code
    normalized_code = provided_code.upper().replace('-', '').replace(' ', '')
    
    for i, stored_code in enumerate(stored_codes):
        # Normalize stored code for comparison
        normalized_stored = stored_code.upper().replace('-', '').replace(' ', '')
        
        if normalized_code == normalized_stored:
            # Remove the used code
            remaining_codes = stored_codes[:i] + stored_codes[i+1:]
            return True, remaining_codes
    
    return False, stored_codes

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
