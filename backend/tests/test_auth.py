import pytest
from fastapi.testclient import TestClient

def test_signup_and_login(client: TestClient):
    # 1. Signup test
    signup_data = {
        "email": "saas_user@example.com",
        "password": "securepassword123"
    }
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["email"] == "saas_user@example.com"
    assert "id" in json_data

    # 2. Login test
    login_data = {
        "username": "saas_user@example.com",
        "password": "securepassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
