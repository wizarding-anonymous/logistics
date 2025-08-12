import uuid
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import KYCDocument, User

def test_submit_kyc_document_success_for_supplier(
    client: TestClient, auth_token_factory, test_user: dict
):
    """
    Test that a logged-in user with the 'supplier' role can submit a KYC document.
    """
    token = auth_token_factory(user_id=test_user["id"], roles=["supplier"])
    headers = {"Authorization": f"Bearer {token}"}

    doc_payload = {
        "document_type": "inn",
        "file_storage_key": "path/to/inn.pdf"
    }

    response = client.post("/api/v1/auth/users/me/kyc-documents", headers=headers, json=doc_payload)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["document_type"] == "inn"
    assert data["status"] == "pending"
    assert data["user_id"] == str(test_user["id"])

def test_submit_kyc_document_fails_for_client(
    client: TestClient, auth_token_factory, test_user: dict
):
    """
    Test that a user with the default 'client' role cannot submit a KYC document.
    """
    token = auth_token_factory(user_id=test_user["id"], roles=["client"])
    headers = {"Authorization": f"Bearer {token}"}

    doc_payload = {
        "document_type": "passport",
        "file_storage_key": "path/to/passport.jpg"
    }

    response = client.post("/api/v1/auth/users/me/kyc-documents", headers=headers, json=doc_payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "Only users with the 'supplier' role can submit KYC documents."

def test_list_my_kyc_documents(
    client: TestClient, auth_token_factory, test_user: dict, test_db_session: AsyncSession
):
    """
    Test that a user can list their own submitted KYC documents.
    """
    # Setup: Create a document first
    user_id_uuid = uuid.UUID(test_user["id"])
    db_doc = KYCDocument(user_id=user_id_uuid, document_type="ogrn", file_storage_key="test/key.pdf")
    test_db_session.add(db_doc)
    test_db_session.commit()

    # The test
    token = auth_token_factory(user_id=test_user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/users/me/kyc-documents", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check if the document we just created is in the list
    assert any(d["document_type"] == "ogrn" and d["file_storage_key"] == "test/key.pdf" for d in data)
