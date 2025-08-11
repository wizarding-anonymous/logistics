import uuid
from fastapi.testclient import TestClient
from rfq.models import RFQ

def test_list_open_rfqs_as_supplier(client: TestClient, auth_token_factory, test_user_id):
    """
    Test that a user with a 'supplier' role can list open RFQs.
    """
    token = auth_token_factory(user_id=test_user_id, roles=["supplier"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/open-rfqs", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_open_rfqs_as_client_forbidden(client: TestClient, auth_token_factory, test_user_id):
    """
    Test that a user with a 'client' role CANNOT list open RFQs.
    """
    token = auth_token_factory(user_id=test_user_id, roles=["client"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/open-rfqs", headers=headers)
    assert response.status_code == 403 # Forbidden

def test_submit_offer_as_supplier(client: TestClient, auth_token_factory, test_db):
    """
    Test that a supplier can submit an offer to an open RFQ.
    """
    import asyncio
    from models import RFQ

    # Setup: Create an open RFQ
    client_user_id = uuid.uuid4()
    client_org_id = uuid.uuid4()
    rfq_id = uuid.uuid4()
    async def add_rfq():
        async with test_db() as session:
            db_rfq = RFQ(id=rfq_id, user_id=client_user_id, organization_id=client_org_id, status='open')
            session.add(db_rfq)
            await session.commit()
    asyncio.run(add_rfq())

    # The Test
    supplier_user_id = uuid.uuid4()
    supplier_org_id = uuid.uuid4()
    token = auth_token_factory(user_id=supplier_user_id, roles=["supplier"], org_id=supplier_org_id)
    headers = {"Authorization": f"Bearer {token}"}

    offer_payload = {"price_amount": 500.50, "price_currency": "USD"}

    response = client.post(f"/{rfq_id}/offers", headers=headers, json=offer_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["price_amount"] == 500.50
    assert data["supplier_organization_id"] == str(supplier_org_id)
    assert data["rfq_id"] == str(rfq_id)
