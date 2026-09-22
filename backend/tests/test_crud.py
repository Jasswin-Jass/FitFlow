import pytest
from datetime import date, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crud_entities(client: AsyncClient):
    # Setup test gym
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "CRUD Test Gym",
            "owner_name": "Test Owner",
            "email": "crud.owner@testgym.com",
            "password": "Password123!",
        },
    )
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Trainers CRUD
    tr_create = await client.post(
        "/api/v1/trainers",
        headers=headers,
        json={"name": "Coach Ram", "email": "ram@testgym.com", "specialty": "Kettlebells"},
    )
    assert tr_create.status_code == 201
    tr_id = tr_create.json()["id"]

    tr_list = await client.get("/api/v1/trainers", headers=headers)
    assert tr_list.status_code == 200
    assert any(t["id"] == tr_id for t in tr_list.json()["items"])

    tr_update = await client.patch(
        f"/api/v1/trainers/{tr_id}",
        headers=headers,
        json={"specialty": "Olympic Lifting"},
    )
    assert tr_update.status_code == 200
    assert tr_update.json()["specialty"] == "Olympic Lifting"

    # 2. Membership Plans CRUD
    plan_resp = await client.post(
        "/api/v1/membership-plans",
        headers=headers,
        json={"name": "Gold 3-Month", "price": 4500.0, "duration_days": 90},
    )
    assert plan_resp.status_code == 201
    plan_id = plan_resp.json()["id"]

    # 3. Members CRUD
    mem_resp = await client.post(
        "/api/v1/members",
        headers=headers,
        json={
            "name": "Saravanan K",
            "email": "saravanan.k@gmail.com",
            "phone": "+91 98888 11111",
            "status": "active",
        },
    )
    assert mem_resp.status_code == 201
    mem_id = mem_resp.json()["id"]

    # Test search & status filter
    search_resp = await client.get("/api/v1/members?search=Saravanan", headers=headers)
    assert search_resp.status_code == 200
    assert len(search_resp.json()["items"]) == 1

    # 4. Membership & Auto-Payment Creation
    mship_resp = await client.post(
        "/api/v1/memberships",
        headers=headers,
        json={
            "member_id": mem_id,
            "plan_id": plan_id,
            "create_payment": True,
        },
    )
    assert mship_resp.status_code == 201
    mship_id = mship_resp.json()["id"]
    assert mship_resp.json()["status"] == "active"
    assert mship_resp.json()["plan_price"] == 4500.0

    # Verify auto-recorded payment exists
    payments_resp = await client.get("/api/v1/payments", headers=headers)
    assert payments_resp.status_code == 200
    assert any(p["member_id"] == mem_id and p["amount"] == 4500.0 for p in payments_resp.json()["items"])

    # 5. Membership Renewal
    renew_resp = await client.post(
        f"/api/v1/memberships/{mship_id}/renew",
        headers=headers,
        json={"create_payment": True},
    )
    assert renew_resp.status_code == 200
    assert renew_resp.json()["member_id"] == mem_id
