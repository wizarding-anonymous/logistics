import uuid
from fastapi.testclient import TestClient

def test_create_rfq(
    client: TestClient,
    test_user_id: uuid.UUID,
    test_org_id: uuid.UUID,
    auth_token_factory,
):
    """
    Test that a logged-in user can successfully create a new RFQ.
    """
    token = auth_token_factory(user_id=test_user_id)
    headers = {"Authorization": f"Bearer {token}"}

    rfq_payload = {
        "cargo": {
            "description": "Test Cargo"
        },
        "segments": [
            {
                "origin_address": "New York, USA",
                "destination_address": "London, UK"
            }
        ]
    }

    response = client.post(f"/?org_id={test_org_id}", headers=headers, json=rfq_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["organization_id"] == str(test_org_id)
    assert data["user_id"] == str(test_user_id)
    assert data["cargo"]["description"] == "Test Cargo"
    assert len(data["segments"]) == 1
    assert data["segments"][0]["origin_address"] == "New York, USA"


def test_list_rfqs(
    client: TestClient,
    test_user_id: uuid.UUID,
    test_org_id: uuid.UUID,
    auth_token_factory,
    test_db, # To create an RFQ first
):
    """
    Test that a user can list RFQs for their organization.
    """
    import asyncio
    from models import RFQ, Cargo, ShipmentSegment

    # Setup: Create an RFQ in the database first
    async def add_rfq():
        async with test_db() as session:
            db_rfq = RFQ(user_id=test_user_id, organization_id=test_org_id)
            db_rfq.cargo = Cargo(description="My test cargo")
            db_rfq.segments.append(ShipmentSegment(origin_address="A", destination_address="B", sequence=1))
            session.add(db_rfq)
            await session.commit()

    asyncio.run(add_rfq())

    # The Test
    token = auth_token_factory(user_id=test_user_id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/?org_id={test_org_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["organization_id"] == str(test_org_id)
    assert data[0]["cargo"]["description"] == "My test cargo"
