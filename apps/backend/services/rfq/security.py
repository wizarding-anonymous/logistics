import os
from typing import Optional
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# This MUST be the same secret key used by the auth service
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_long_and_random")
ALGORITHM = "HS256"

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def decode_token(token: str) -> Optional[dict]:
    """
    Decodes a JWT token. Returns the payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def require_supplier_role(token: str = Depends(oauth2_scheme)):
    """
    Dependency that checks if the authenticated user has the 'supplier' role.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have the required 'supplier' role.",
    )
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    roles = payload.get("roles", [])
    if "supplier" not in roles:
        raise credentials_exception
    return payload
