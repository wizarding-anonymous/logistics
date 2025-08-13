import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Query
from pydantic import BaseModel

# This secret key should be consistent across all microservices
# and loaded securely from environment variables.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_long_and_random")
ALGORITHM = "HS256"

def decode_token(token: str) -> Optional[dict]:
    """Decodes a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

class UserContext(BaseModel):
    """Pydantic model to represent the user data extracted from the JWT."""
    id: uuid.UUID
    roles: List[str]
    org_id: Optional[uuid.UUID] = None

async def get_user_context_from_query(token: str = Query(...)) -> UserContext:
    """
    Dependency to get user context from a token passed as a query parameter.
    This is useful for authenticating WebSockets.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if token is None:
        raise credentials_exception

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
