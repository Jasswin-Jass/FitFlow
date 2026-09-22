import pytest
from datetime import date, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_and_recomputation_pipeline(client: AsyncClient):
    # 1. Register new gym -> verify empty state
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Analytics Gym",
            "owner_name": "Metrics Master",
            "email": "analytics@fitflowgym.com",
            "password": "Password123!",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_init = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert dash_init.status_code == 200
    d_data = dash_init.json()
    assert d_data["active_members"]["value"] == 0
    assert d_data["mrr"]["value"] == 0.0
    assert d_data["at_risk_members"]["value"] == 0

    # 2. Add Plan: ₹3,000 for 30 days (Normalized monthly = ₹3,000)
    p_resp = await client.post(
        "/api/v1/membership-plans",
        headers=headers,
        json={"name": "Monthly Standard", "price": 3000.0, "duration_days": 30},
    )
    plan_id = p_resp.json()["id"]

    # 3. Add Member 1: Active healthy member
    m1 = await client.post(
        "/api/v1/members",
        headers=headers,
        json={"name": "Healthy Member", "email": "m1@fitflowgym.com", "phone": "+91 91111 22222"},
    )
    m1_id = m1.json()["id"]
    await client.post(
        "/api/v1/memberships",
        headers=headers,
        json={"member_id": m1_id, "plan_id": plan_id, "start_date": str(date.today() - timedelta(days=5))},
    )

    # 4. Add Member 2: At-risk member (expiring in 2 days)
    m2 = await client.post(
        "/api/v1/members",
        headers=headers,
        json={"name": "Expiring Member", "email": "m2@fitflowgym.com", "phone": "+91 92222 33333"},
    )
    m2_id = m2.json()["id"]
    await client.post(
        "/api/v1/memberships",
        headers=headers,
        json={"member_id": m2_id, "plan_id": plan_id, "start_date": str(date.today() - timedelta(days=28))},
    )

    # 5. Add Member 3: At-risk member (recent failed payment)
    m3 = await client.post(
        "/api/v1/members",
        headers=headers,
        json={"name": "Failed Payment Member", "email": "m3@fitflowgym.com", "phone": "+91 93333 44444"},
    )
    m3_id = m3.json()["id"]
    m3_ship = await client.post(
        "/api/v1/memberships",
        headers=headers,
        json={"member_id": m3_id, "plan_id": plan_id, "create_payment": False},
    )
    # Record failed payment
    await client.post(
        "/api/v1/payments",
        headers=headers,
        json={
            "member_id": m3_id,
            "membership_id": m3_ship.json()["id"],
            "amount": 3000.0,
            "status": "failed",
        },
    )

    # 6. Trigger recompute-metrics
    recompute_resp = await client.post("/api/v1/admin/recompute-metrics", headers=headers)
    assert recompute_resp.status_code == 200
    recomp_data = recompute_resp.json()

    # Verify: 3 active members, ₹9,000 MRR (3 * ₹3,000), 2 at-risk members
    assert recomp_data["active_members"]["value"] == 3
    assert recomp_data["mrr"]["value"] == 9000.0
    assert recomp_data["at_risk_members"]["value"] == 2
    assert len(recomp_data["at_risk_list"]) == 2
    assert any("expiring" in item["risk_reason"].lower() for item in recomp_data["at_risk_list"])
    assert any("failed payment" in item["risk_reason"].lower() for item in recomp_data["at_risk_list"])
