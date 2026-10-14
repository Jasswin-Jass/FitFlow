import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_public_member_signup_requires_successful_payment(client: AsyncClient):
    reg_payload = {
        "gym_name": "Public Signup Gym",
        "owner_name": "Ishaan Rao",
        "email": "ishaan@publicsignup.com",
        "password": "SecurePassword123!",
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200, reg_resp.text
    gym_id = reg_resp.json()["user"]["gym_id"]
    token = reg_resp.json()["access_token"]

    create_plan_resp = await client.post(
        "/api/v1/membership-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Starter Plus",
            "description": "For new members",
            "price": 1499,
            "duration_days": 30,
            "status": "active",
        },
    )
    assert create_plan_resp.status_code == 201, create_plan_resp.text
    plan_id = create_plan_resp.json()["id"]

    signup_payload = {
        "gym_id": gym_id,
        "plan_id": plan_id,
        "member": {
            "name": "Aarav Patel",
            "first_name": "Aarav",
            "last_name": "Patel",
            "email": "aarav.patel@example.com",
            "phone": "9876543210",
            "city": "Bengaluru",
            "fitness_goal": "Weight Loss",
            "status": "active",
        },
        "payment_method": "upi",
        "payment_status": "success",
    }

    signup_resp = await client.post("/api/v1/public/member-signup", json=signup_payload)
    assert signup_resp.status_code == 200, signup_resp.text
    body = signup_resp.json()
    assert body["member"]["email"] == "aarav.patel@example.com"
    assert body["membership"]["plan_id"] == plan_id
    assert body["payment"]["status"] == "paid"

    failed_signup = {
        **signup_payload,
        "member": {**signup_payload["member"], "email": "failed.member@example.com"},
        "payment_status": "failed",
    }
    failed_resp = await client.post("/api/v1/public/member-signup", json=failed_signup)
    assert failed_resp.status_code == 400
    assert failed_resp.json()["detail"] == "Payment must succeed before a public signup is registered."
