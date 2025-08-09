import pytest
import uuid
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock

from apps.backend.services.orgs.api.v1.orgs import require_organization_role, UserContext

@pytest.mark.asyncio
async def test_require_organization_role_success():
    """
    Tests that the dependency allows access when the user has the required role.
    """
    # Mocks
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = "owner"
    mock_db.execute.return_value = mock_result

    user_context = UserContext(id=uuid.uuid4(), email="test@test.com", roles=["some_global_role"])
    org_id = uuid.uuid4()

    # Create the dependency checker
    role_checker_dependency = require_organization_role(required_roles=["owner", "admin"])

    # Run the checker
    # It should complete without raising an exception
    await role_checker_dependency(org_id=org_id, user_context=user_context, db=mock_db)


@pytest.mark.asyncio
async def test_require_organization_role_failure():
    """
    Tests that the dependency raises HTTPException when the user does NOT have the role.
    """
    # Mocks
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = "member" # User is only a member
    mock_db.execute.return_value = mock_result

    user_context = UserContext(id=uuid.uuid4(), email="test@test.com", roles=["some_global_role"])
    org_id = uuid.uuid4()

    # Create the dependency checker
    role_checker_dependency = require_organization_role(required_roles=["owner", "admin"])

    # Assert that the correct exception is raised
    with pytest.raises(HTTPException) as exc_info:
        await role_checker_dependency(org_id=org_id, user_context=user_context, db=mock_db)

    assert exc_info.value.status_code == 403
