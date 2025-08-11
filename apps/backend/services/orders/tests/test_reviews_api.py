import uuid
from fastapi.testclient import TestClient
from orders.models import Order, OrderStatus

def test_create_review(client: TestClient, auth_token_factory, test_order: Order, test_db):
    """
    Test that the client of a completed order can leave a review.
    """
    import asyncio

    # Setup: Mark the order as completed
    async def complete_order():
        async with test_db() as session:
            test_order.status = OrderStatus.CLOSED
            session.add(test_order)
            await session.commit()
    asyncio.run(complete_order())

    # The Test
    client_user_id = uuid.uuid4()
    # Token's org_id must match the order's client_id
    token = auth_token_factory(user_id=client_user_id, org_id=test_order.client_id)
    headers = {"Authorization": f"Bearer {token}"}

    review_payload = {"rating": 5, "comment": "Excellent service!"}

    response = client.post(f"/orders/{test_order.id}/review", headers=headers, json=review_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Excellent service!"
    assert data["reviewer_id"] == str(client_user_id)

def test_create_review_unauthorized(client: TestClient, auth_token_factory, test_order: Order):
    """
    Test that a random user cannot leave a review on an order.
    """
    unauthorized_user_id = uuid.uuid4()
    unauthorized_org_id = uuid.uuid4()
    token = auth_token_factory(user_id=unauthorized_user_id, org_id=unauthorized_org_id)
    headers = {"Authorization": f"Bearer {token}"}

    review_payload = {"rating": 1, "comment": "I am a random user."}

    response = client.post(f"/orders/{test_order.id}/review", headers=headers, json=review_payload)

    assert response.status_code == 403 # Forbidden
