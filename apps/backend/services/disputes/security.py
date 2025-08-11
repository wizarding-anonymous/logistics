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

def get_current_user_context(token: str = Depends(oauth2_scheme)) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    org_id = payload.get("org_id")
    roles = payload.get("roles", [])

    if user_id is None or org_id is None:
        raise HTTPException(status_code=403, detail="Incomplete user context in token.")

    return {
        "user_id": uuid.UUID(user_id),
        "org_id": uuid.UUID(org_id),
        "roles": roles
    }

def require_admin_role(user_context: dict = Depends(get_current_user_context)):
    """
    Dependency that checks if the authenticated user has the 'admin' role.
    """
    if "admin" not in user_context["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin privileges.",
        )
    return user_context
