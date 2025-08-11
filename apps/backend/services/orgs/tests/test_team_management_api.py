import uuid
from fastapi.testclient import TestClient
from orgs.models import Organization

def test_list_organization_members(
    client: TestClient,
    test_organization: Organization,
    test_user_owner: dict,
    auth_token_factory,
):
    """
    Test that an organization owner can list the members of their organization.
    """
    token = auth_token_factory(user_id=test_user_owner["id"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/{test_organization.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Corp"
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == str(test_user_owner["id"])
    assert data["members"][0]["role"] == "owner"


def test_invite_member(
    client: TestClient,
    test_organization: Organization,
    test_user_owner: dict,
    auth_token_factory,
):
    """
    Test that an owner can successfully invite a new member.
    """
    token = auth_token_factory(user_id=test_user_owner["id"])
    headers = {"Authorization": f"Bearer {token}"}

    invite_email = "new.member@example.com"
    invite_payload = {"email": invite_email, "role": "member"}

    response = client.post(f"/organizations/{test_organization.id}/invitations", headers=headers, json=invite_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == invite_email
    assert data["role"] == "member"
    assert data["status"] == "pending"
    assert data["organization_id"] == str(test_organization.id)


def test_remove_member(
    client: TestClient,
    test_organization: Organization,
    test_user_owner: dict,
    auth_token_factory,
    test_db, # Need db session to add another member to remove
):
    """
    Test that an owner can remove another member from the organization.
    """
    import asyncio
    from ..models import user_organization_link

    # Setup: Add a second member to the organization to be removed
    user_to_remove_id = uuid.uuid4()
    async def add_member():
        async with test_db() as session:
            stmt = user_organization_link.insert().values(
                user_id=user_to_remove_id,
                organization_id=test_organization.id,
                role="member"
            )
            await session.execute(stmt)
            await session.commit()

    asyncio.run(add_member())

    # The Test
    token = auth_token_factory(user_id=test_user_owner["id"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f"/organizations/{test_organization.id}/members/{user_to_remove_id}", headers=headers)

    assert response.status_code == 204

    # Verification: Check that the member was actually removed
    response = client.get(f"/{test_organization.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["members"]) == 1 # Only the owner should be left
    assert data["members"][0]["user_id"] == str(test_user_owner["id"])
