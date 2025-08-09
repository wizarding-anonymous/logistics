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
