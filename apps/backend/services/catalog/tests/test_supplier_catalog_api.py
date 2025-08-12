import uuid
from fastapi.testclient import TestClient
from catalog.models import ServiceOffering

def test_create_service_offering(client: TestClient, auth_token_factory, test_supplier_user):
    """
    Test that a supplier can create a service offering.
    """
    token = auth_token_factory(
        user_id=test_supplier_user["id"],
        org_id=test_supplier_user["org_id"],
        roles=["supplier"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    service_payload = {
        "name": "My FTL Service",
        "service_type": "FTL",
        "is_active": True,
        "tariffs": [{"price": 1.5, "currency": "USD", "unit": "per_km"}]
    }

    response = client.post("/services", headers=headers, json=service_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My FTL Service"
    assert data["supplier_organization_id"] == str(test_supplier_user["org_id"])


def test_list_my_services(client: TestClient, auth_token_factory, test_supplier_user, test_db):
    """
    Test that a supplier can list their own services.
    """
    import asyncio
    from models import ServiceOffering

    # Setup: Create a service offering for the supplier
    async def add_service():
        async with test_db() as session:
            service = ServiceOffering(
                name="My Other Service",
                service_type="LTL",
                supplier_organization_id=test_supplier_user["org_id"]
            )
            session.add(service)
            await session.commit()
    asyncio.run(add_service())

    # The Test
    token = auth_token_factory(
        user_id=test_supplier_user["id"],
        org_id=test_supplier_user["org_id"],
        roles=["supplier"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/supplier/services", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "My Other Service"
