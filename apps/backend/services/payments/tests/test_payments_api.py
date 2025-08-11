import uuid
from fastapi.testclient import TestClient
from payments.models import Invoice, InvoiceStatus

def test_list_my_invoices(client: TestClient, auth_token_factory, test_invoice: Invoice):
    """
    Test that a user can list invoices belonging to their organization.
    """
    user_id = uuid.uuid4()
    # Token's org_id must match the invoice's organization_id
    token = auth_token_factory(user_id=user_id, org_id=test_invoice.organization_id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/invoices", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(test_invoice.id)

def test_pay_invoice(client: TestClient, auth_token_factory, test_invoice: Invoice):
    """
    Test that a user can pay an invoice belonging to their organization.
    """
    user_id = uuid.uuid4()
    # Token's org_id must match the invoice's organization_id
    token = auth_token_factory(user_id=user_id, org_id=test_invoice.organization_id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/invoices/{test_invoice.id}/pay", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == InvoiceStatus.PAID.value
