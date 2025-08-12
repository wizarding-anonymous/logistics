import uuid
from fastapi.testclient import TestClient
from rfq.models import RFQ, Offer

def test_accept_offer(client: TestClient, auth_token_factory, test_db):
    """
    Test the full workflow of creating an RFQ, making an offer, and accepting it.
    """
    import asyncio
    from models import RFQ, Offer

    # 1. Setup users and get tokens
    client_user_id = uuid.uuid4()
    client_org_id = uuid.uuid4()
    supplier_user_id = uuid.uuid4()
    supplier_org_id = uuid.uuid4()

    client_token = auth_token_factory(user_id=client_user_id, roles=["client"])
    supplier_token = auth_token_factory(user_id=supplier_user_id, roles=["supplier"], org_id=supplier_org_id)

    # 2. Client creates an RFQ
    rfq_payload = {
        "cargo": {"description": "Acceptance Test Cargo"},
        "segments": [{"origin_address": "A", "destination_address": "B"}]
    }
    response = client.post(f"/?org_id={client_org_id}", headers={"Authorization": f"Bearer {client_token}"}, json=rfq_payload)
    assert response.status_code == 201
    rfq_data = response.json()
    rfq_id = rfq_data["id"]

    # 3. Supplier makes an offer
    offer_payload = {"price_amount": 123.45, "price_currency": "USD"}
    response = client.post(f"/{rfq_id}/offers", headers={"Authorization": f"Bearer {supplier_token}"}, json=offer_payload)
    assert response.status_code == 201
    offer_data = response.json()
    offer_id = offer_data["id"]

    # 4. Client accepts the offer
    # TODO: This requires an authz check that the user accepting is in the client_org_id
    # For now, the endpoint just requires a logged-in user.
    response = client.post(f"/offers/{offer_id}/accept", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 200

    accepted_offer_data = response.json()
    assert accepted_offer_data["status"] == "accepted"

    # 5. Verify the RFQ is now closed
    response = client.get(f"/{rfq_id}", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 200
    rfq_data = response.json()
    assert rfq_data["status"] == "closed"
