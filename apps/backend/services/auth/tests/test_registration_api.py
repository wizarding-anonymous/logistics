from fastapi.testclient import TestClient

def test_register_supplier(client: TestClient):
    """
    Test that a user can register with the 'supplier' role.
    """
    user_payload = {
        "email": "supplier@example.com",
        "password": "ValidPassword1!",
        "roles": ["supplier"],
        "recaptcha_token": "mock_token" # Assuming reCAPTCHA is mocked or disabled in test
    }

    response = client.post("/register", json=user_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "supplier@example.com"
    assert "supplier" in data["roles"]
    assert "client" not in data["roles"]
