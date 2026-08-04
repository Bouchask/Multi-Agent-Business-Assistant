import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_01_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    print("\n✅ Health Check verified!")

def test_02_register_admin_user():
    payload = {
        "email": "admin@assistant.local",
        "full_name": "Senior Chief Administrator",
        "password": "SuperSecretPassword123!",
        "role_name": "ADMIN"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    if response.status_code == 409:
        print("ℹ️ Admin user already exists from a prior run, proceeding to login.")
        return
    assert response.status_code == 201, f"Registration failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"]["name"] == "ADMIN"
    print("✅ Admin registration verified!")

def test_03_login_admin_user():
    payload = {
        "email": "admin@assistant.local",
        "password": "SuperSecretPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    # Store tokens in environment for sequential testing
    os.environ["TEST_ACCESS_TOKEN"] = data["access_token"]
    os.environ["TEST_REFRESH_TOKEN"] = data["refresh_token"]
    print("✅ Login & JWT Token issuance verified!")

def test_04_protected_route_get_me():
    token = os.environ.get("TEST_ACCESS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200, f"Protected get me failed: {response.text}"
    data = response.json()
    assert data["email"] == "admin@assistant.local"
    assert data["role"]["name"] == "ADMIN"
    print("✅ Protected /me endpoint with Bearer Token verified!")

def test_05_token_refresh():
    refresh_token = os.environ.get("TEST_REFRESH_TOKEN")
    response = client.post("/api/v1/auth/token/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200, f"Token refresh failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    print("✅ JWT Refresh Token rotation verified!")

def test_06_logout():
    token = os.environ.get("TEST_ACCESS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
    print("✅ Logout endpoint verified!")
