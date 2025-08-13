import os
import uuid
import yaml
from datetime import datetime, timedelta
from typing import Optional, List, Set, Dict
from functools import lru_cache
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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

# --- RBAC Implementation ---

RBAC_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'rbac-matrix.yaml')

@lru_cache()
def get_rbac_matrix() -> Dict[str, Set[str]]:
    """Loads and parses the RBAC YAML file."""
    try:
        with open(RBAC_FILE_PATH, 'r') as f:
            rbac_data = yaml.safe_load(f)
    except FileNotFoundError:
        return {}

    role_permissions = {}
    permissions_map = {p['id']: p for p in rbac_data.get('permissions', [])}

    for role in rbac_data.get('roles', []):
        role_name = role['name']
        if role_name == 'admin':
            role_permissions[role_name] = set(permissions_map.keys())
            continue
        permissions = set(role.get('permissions', []))
        role_permissions[role_name] = permissions
    return role_permissions

class UserContext(BaseModel):
    """Pydantic model for user data from JWT."""
    id: uuid.UUID
    roles: List[str]
    org_id: Optional[uuid.UUID] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user_context(token: str = Depends(oauth2_scheme)) -> UserContext:
    """Dependency to get user context from JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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
    """Dependency factory to check for a specific permission."""
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

def require_supplier_role(user_context: UserContext = Depends(get_current_user_context)):
    """A specific dependency to check for the 'supplier' role."""
    if "supplier" not in user_context.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supplier role required."
        )
    return user_context
