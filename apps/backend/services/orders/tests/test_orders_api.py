import uuid
from fastapi.testclient import TestClient
from orders.models import Order, OrderStatus

def test_update_order_status(client: TestClient, auth_token_factory, test_order: Order):
    """
    Test that the assigned supplier can update the order status.
    """
    supplier_user_id = uuid.uuid4()
    # The token's org_id must match the order's supplier_id for the authz check to pass
    token = auth_token_factory(
        user_id=supplier_user_id,
        org_id=test_order.supplier_id,
        roles=["supplier"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    status_payload = {
        "status": OrderStatus.IN_TRANSIT.value,
        "notes": "Shipment has left the warehouse."
    }

    response = client.patch(f"/orders/{test_order.id}/status", headers=headers, json=status_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_transit"

    # Verify that a history event was created
    assert len(data["status_history"]) > 0
    assert data["status_history"][-1]["status"] == "in_transit"
    assert data["status_history"][-1]["notes"] == "Shipment has left the warehouse."

def test_update_order_status_unauthorized(client: TestClient, auth_token_factory, test_order: Order):
    """
    Test that a non-assigned supplier cannot update the order status.
    """
    unauthorized_supplier_org_id = uuid.uuid4()
    token = auth_token_factory(
        user_id=uuid.uuid4(),
        org_id=unauthorized_supplier_org_id,
        roles=["supplier"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    status_payload = {"status": OrderStatus.IN_TRANSIT.value}

    response = client.patch(f"/orders/{test_order.id}/status", headers=headers, json=status_payload)

    assert response.status_code == 403
