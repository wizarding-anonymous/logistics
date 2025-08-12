import uuid
from fastapi.testclient import TestClient
from admin.models import User, KYCStatus

def test_list_pending_kyc_as_admin(client: TestClient, auth_token_factory, pending_user: User):
    """
    Test that an admin can list users with pending KYC documents.
    """
    admin_user_id = uuid.uuid4()
    token = auth_token_factory(user_id=admin_user_id, roles=["admin"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/kyc/pending", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(pending_user.id)
    assert len(data[0]["kyc_documents"]) == 1
    assert data[0]["kyc_documents"][0]["status"] == "pending"

def test_approve_kyc_document(client: TestClient, auth_token_factory, pending_user: User):
    """
    Test that an admin can approve a KYC document.
    """
    admin_user_id = uuid.uuid4()
    token = auth_token_factory(user_id=admin_user_id, roles=["admin"])
    headers = {"Authorization": f"Bearer {token}"}

    doc_to_approve = pending_user.kyc_documents[0]

    response = client.post(f"/kyc/documents/{doc_to_approve.id}/approve", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == KYCStatus.APPROVED.value

def test_reject_kyc_document(client: TestClient, auth_token_factory, pending_user: User):
    """
    Test that an admin can reject a KYC document.
    """
    admin_user_id = uuid.uuid4()
    token = auth_token_factory(user_id=admin_user_id, roles=["admin"])
    headers = {"Authorization": f"Bearer {token}"}

    doc_to_reject = pending_user.kyc_documents[0]
    rejection_payload = {"reason": "Document is blurry."}

    response = client.post(f"/kyc/documents/{doc_to_reject.id}/reject", headers=headers, json=rejection_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == KYCStatus.REJECTED.value
    assert data["rejection_reason"] == "Document is blurry."
