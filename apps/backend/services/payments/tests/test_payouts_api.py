import uuid
from fastapi.testclient import TestClient
from payments.models import Payout, PayoutStatus

def test_approve_payout(client: TestClient, auth_token_factory, test_db):
    """
    Test that an admin can approve a pending payout.
    """
    import asyncio

    # Setup: Create a pending payout in the database
    payout_id = uuid.uuid4()
    async def add_pending_payout():
        async with test_db() as session:
            db_payout = Payout(
                id=payout_id,
                supplier_organization_id=uuid.uuid4(),
                order_id=uuid.uuid4(),
                amount=100.00,
                currency="USD",
                status=PayoutStatus.PENDING
            )
            session.add(db_payout)
            await session.commit()
    asyncio.run(add_pending_payout())

    # The Test
    admin_user_id = uuid.uuid4()
    admin_org_id = uuid.uuid4() # Admin's org doesn't matter for this
    token = auth_token_factory(user_id=admin_user_id, org_id=admin_org_id, roles=["admin"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/payouts/{payout_id}/approve", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == PayoutStatus.COMPLETED.value
    assert data["id"] == str(payout_id)
