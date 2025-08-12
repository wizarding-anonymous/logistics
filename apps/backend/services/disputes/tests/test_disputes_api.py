import uuid
from fastapi.testclient import TestClient

def test_open_dispute(client: TestClient, auth_token_factory, test_user_context):
    """
    Test that a user can open a dispute for an order.
    """
    token = auth_token_factory(
        user_id=test_user_context["user_id"],
        org_id=test_user_context["org_id"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    dispute_payload = {
        "order_id": str(uuid.uuid4()),
        "reason": "The shipment was damaged."
    }

    response = client.post("/", headers=headers, json=dispute_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["opened_by_id"] == str(test_user_context["user_id"])
    assert data["status"] == "open"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "The shipment was damaged."

def test_add_dispute_message(client: TestClient, auth_token_factory, test_user_context, test_db):
    """
    Test that a user can add a message to an existing dispute.
    """
    import asyncio
    from disputes.models import Dispute

    # Setup: Create a dispute first
    dispute_id = uuid.uuid4()
    async def add_dispute():
        async with test_db() as session:
            db_dispute = Dispute(id=dispute_id, order_id=uuid.uuid4(), opened_by_id=uuid.uuid4())
            session.add(db_dispute)
            await session.commit()
    asyncio.run(add_dispute())

    # The Test
    token = auth_token_factory(
        user_id=test_user_context["user_id"],
        org_id=test_user_context["org_id"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    message_payload = {"content": "Here is a photo of the damage."}

    response = client.post(f"/{dispute_id}/messages", headers=headers, json=message_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Here is a photo of the damage."
    assert data["dispute_id"] == str(dispute_id)
