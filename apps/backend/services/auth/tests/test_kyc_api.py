import uuid
from fastapi.testclient import TestClient
from auth.models import KYCDocument

def test_submit_kyc_document(client: TestClient, auth_token_factory, test_user):
    """
    Test that a logged-in user can submit a KYC document.
    """
    token = auth_token_factory(user_id=test_user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    doc_payload = {
        "document_type": "inn",
        "file_storage_key": "path/to/inn.pdf"
    }

    response = client.post("/users/me/kyc-documents", headers=headers, json=doc_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["document_type"] == "inn"
    assert data["status"] == "pending"
    assert data["user_id"] == str(test_user["id"])

def test_list_my_kyc_documents(client: TestClient, auth_token_factory, test_user, test_db):
    """
    Test that a user can list their own submitted KYC documents.
    """
    import asyncio
    from models import KYCDocument

    # Setup: Create a document first
    async def add_doc():
        async with test_db() as session:
            db_doc = KYCDocument(user_id=test_user["id"], document_type="ogrn", file_storage_key="key")
            session.add(db_doc)
            await session.commit()
    asyncio.run(add_doc())

    # The test
    token = auth_token_factory(user_id=test_user["id"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/me/kyc-documents", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["document_type"] == "ogrn"
