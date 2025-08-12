import os
from typing import Optional, Dict
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import uuid

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_long_and_random")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def decode_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def require_admin_role(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Dependency to decode JWT and ensure the user has the 'admin' role.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have admin privileges.",
    )
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    roles = payload.get("roles", [])
    if "admin" not in roles:
        raise credentials_exception

    return payload
