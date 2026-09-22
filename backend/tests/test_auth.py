import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # 1. Register a new Gym
    reg_payload = {
        "gym_name": "Olympus Gym",
        "owner_name": "Vikram Seth",
        "email": "vikram@olympusgym.com",
        "password": "SecurePassword123!",
    }
    resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "vikram@olympusgym.com"
    assert data["user"]["role"] == "owner"
    assert data["user"]["gym_name"] == "Olympus Gym"
    token = data["access_token"]

    # 2. Login with valid credentials
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "vikram@olympusgym.com", "password": "SecurePassword123!"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data

    # 3. Login with invalid password
    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "vikram@olympusgym.com", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
    assert bad_login.json()["error"] == "AuthenticationFailed"

    # 4. Check /auth/me with Bearer token
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "vikram@olympusgym.com"
    assert me_data["role"] == "owner"


@pytest.mark.asyncio
async def test_duplicate_registration_prevented(client: AsyncClient):
    reg_payload = {
        "gym_name": "Duplicate Test Gym",
        "owner_name": "Rahul Roy",
        "email": "rahul.roy@dupcheck.com",
        "password": "Password123!",
    }
    first = await client.post("/api/v1/auth/register", json=reg_payload)
    assert first.status_code == 200

    second = await client.post("/api/v1/auth/register", json=reg_payload)
    assert second.status_code == 400
    assert second.json()["error"] == "EmailAlreadyExists"
