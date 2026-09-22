import pytest
from datetime import date, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_bi_analytics_endpoints(client: AsyncClient):
    # 1. Register Gym BI Alpha
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Gym BI Alpha",
            "owner_name": "Alpha Owner",
            "email": "owner@bialpha.com",
            "password": "AlphaPassword123!",
        },
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add Plan: ₹2,000 for 30 days
    plan_resp = await client.post(
        "/api/v1/membership-plans",
        headers=headers,
        json={"name": "Standard Monthly", "price": 2000.0, "duration_days": 30},
    )
    assert plan_resp.status_code == 201
    plan_id = plan_resp.json()["id"]

    # 3. Add Trainer
    trainer_resp = await client.post(
        "/api/v1/trainers",
        headers=headers,
        json={
            "name": "Trainer Alex",
            "email": "alex@bialpha.com",
            "phone": "+91 98888 11111",
            "specialty": "Strength Training",
            "years_of_experience": 5,
            "max_client_capacity": 20,
            "rating": 4.8,
        },
    )
    assert trainer_resp.status_code == 201
    trainer_id = trainer_resp.json()["id"]

    # 4. Add Member 1: Female, Age 28 (DOB: 1998-05-15)
    mem1_resp = await client.post(
        "/api/v1/members",
        headers=headers,
        json={
            "name": "Priya Sharma",
            "first_name": "Priya",
            "last_name": "Sharma",
            "email": "priya@bialpha.com",
            "phone": "+91 98888 22222",
            "date_of_birth": "1998-05-15",
            "gender": "Female",
            "occupation": "Software Engineer",
            "city": "Chennai",
            "preferred_training_time": "Morning",
            "fitness_goal": "Weight Loss",
            "acquisition_source": "Social Media",
            "trainer_id": trainer_id,
            "status": "active",
        },
    )
    assert mem1_resp.status_code == 201
    mem1_id = mem1_resp.json()["id"]
    assert mem1_resp.json()["age"] is not None

    # Assign membership to Member 1 (starts 10 days ago, active)
    mship1_resp = await client.post(
        "/api/v1/memberships",
        headers=headers,
        json={
            "member_id": mem1_id,
            "plan_id": plan_id,
            "start_date": str(date.today() - timedelta(days=10)),
            "create_payment": True,
        },
    )
    assert mship1_resp.status_code == 201

    # 5. Add Member 2: Male, Age 32 (DOB: 1994-08-20), At-risk (expiring in 3 days)
    mem2_resp = await client.post(
        "/api/v1/members",
        headers=headers,
        json={
            "name": "Karthik Raja",
            "first_name": "Karthik",
            "last_name": "Raja",
            "email": "karthik@bialpha.com",
            "phone": "+91 98888 33333",
            "date_of_birth": "1994-08-20",
            "gender": "Male",
            "occupation": "Data Analyst",
            "city": "Chennai",
            "preferred_training_time": "Evening",
            "fitness_goal": "Muscle Gain",
            "acquisition_source": "Referral",
            "trainer_id": trainer_id,
            "status": "active",
        },
    )
    assert mem2_resp.status_code == 201
    mem2_id = mem2_resp.json()["id"]

    # Assign membership to Member 2 (expires in 3 days)
    mship2_resp = await client.post(
        "/api/v1/memberships",
        headers=headers,
        json={
            "member_id": mem2_id,
            "plan_id": plan_id,
            "start_date": str(date.today() - timedelta(days=27)),
            "create_payment": True,
        },
    )
    assert mship2_resp.status_code == 201

    # 6. Test Overview Endpoint
    overview_resp = await client.get("/api/v1/analytics/overview", headers=headers)
    assert overview_resp.status_code == 200
    overview = overview_resp.json()
    assert overview["total_members"]["value"] == 2.0
    assert overview["active_members"]["value"] == 2.0
    assert overview["active_percent"]["value"] == 100.0
    assert overview["mrr"]["value"] == 4000.0
    assert overview["at_risk_members"]["value"] == 1.0  # Member 2 is expiring in 3 days

    # 7. Test Member Intelligence Endpoint
    members_resp = await client.get("/api/v1/analytics/members", headers=headers)
    assert members_resp.status_code == 200
    mem_intel = members_resp.json()
    assert mem_intel["total_members"] == 2
    assert mem_intel["active_members"] == 2
    assert mem_intel["expiring_soon_count"] == 1
    assert mem_intel["at_risk_count"] == 1
    assert mem_intel["avg_age"] is not None
    assert mem_intel["avg_lifetime_value"] == 2000.0
    assert len(mem_intel["segments"]) >= 5

    # 8. Test Demographics Endpoint
    demo_resp = await client.get("/api/v1/analytics/demographics", headers=headers)
    assert demo_resp.status_code == 200
    demo = demo_resp.json()
    assert len(demo["gender_distribution"]) >= 2
    assert any(g["gender"] == "Female" and g["count"] == 1 for g in demo["gender_distribution"])
    assert any(g["gender"] == "Male" and g["count"] == 1 for g in demo["gender_distribution"])
    assert len(demo["age_groups"]) == 6
    assert demo["most_represented_age_group"] == "25-34"
    assert demo["total_reported_profiles"] == 2

    # 9. Test Revenue Intelligence Endpoint
    rev_resp = await client.get("/api/v1/analytics/revenue", headers=headers)
    assert rev_resp.status_code == 200
    rev = rev_resp.json()
    assert rev["mrr"] == 4000.0
    assert rev["total_revenue_all_time"] == 4000.0
    assert len(rev["plan_breakdown"]) == 1
    assert rev["plan_breakdown"][0]["active_count"] == 2

    # 10. Test Membership Intelligence Endpoint
    mship_intel_resp = await client.get("/api/v1/analytics/memberships", headers=headers)
    assert mship_intel_resp.status_code == 200
    mship_intel = mship_intel_resp.json()
    assert mship_intel["active_count"] == 2
    assert mship_intel["expiring_7d_count"] == 1
    assert len(mship_intel["lifecycle_funnel"]) >= 4

    # 11. Test Trainer Intelligence Endpoint
    trainer_intel_resp = await client.get("/api/v1/analytics/trainers", headers=headers)
    assert trainer_intel_resp.status_code == 200
    trainer_intel = trainer_intel_resp.json()
    assert trainer_intel["total_trainers"] == 1
    assert trainer_intel["active_trainers"] == 1
    assert trainer_intel["trainers"][0]["assigned_members"] == 2
    assert trainer_intel["trainers"][0]["utilization_percent"] == 10.0  # 2 / 20 = 10%
    assert trainer_intel["trainers"][0]["revenue_generated"] == 4000.0

    # 12. Test Forecast Endpoint
    forecast_resp = await client.get("/api/v1/analytics/forecast", headers=headers)
    assert forecast_resp.status_code == 200
    forecast = forecast_resp.json()
    # Brand new gym with <7 days history returns clean insufficient history response
    assert forecast["has_sufficient_history"] is False
    assert "Insufficient" in forecast["status_message"]

    # 13. Test Actionable Insights Endpoint
    insights_resp = await client.get("/api/v1/analytics/insights", headers=headers)
    assert insights_resp.status_code == 200
    insights = insights_resp.json()
    assert len(insights["insights"]) >= 1


@pytest.mark.asyncio
async def test_renewal_rate_zero_denominator_returns_none(client: AsyncClient):
    # Register fresh gym with zero expired memberships
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Zero Renewal Gym",
            "owner_name": "New Owner",
            "email": "zero.renewal@example.com",
            "password": "Password@2026",
        },
    )
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add plan
    plan_resp = await client.post(
        "/api/v1/membership-plans",
        headers=headers,
        json={"name": "Starter", "price": 1000.0, "duration_days": 30},
    )
    assert plan_resp.status_code == 201
    plan_id = plan_resp.json()["id"]

    # Add member
    mem_resp = await client.post(
        "/api/v1/members",
        headers=headers,
        json={"name": "Fresh Member", "email": "fresh@example.com", "phone": "+91 99999 12345"},
    )
    assert mem_resp.status_code == 201
    mem_id = mem_resp.json()["id"]

    # Assign membership that ends 30 days in the future (not in past 30 days)
    mship_resp = await client.post(
        "/api/v1/memberships",
        headers=headers,
        json={"member_id": mem_id, "plan_id": plan_id},
    )
    assert mship_resp.status_code == 201

    # Check overview: renewal rate MUST be None and formatted as "N/A", NOT 0.0%
    overview_resp = await client.get("/api/v1/analytics/overview", headers=headers)
    assert overview_resp.status_code == 200
    overview = overview_resp.json()
    assert overview["renewal_rate"]["value"] is None
    assert overview["renewal_rate"]["formatted_value"] == "N/A"
    assert "No renewals due" in overview["renewal_rate"]["subtext"]


@pytest.mark.asyncio
async def test_tenant_isolation_analytics(client: AsyncClient):
    # Register Gym 1
    reg_1 = await client.post(
        "/api/v1/auth/register",
        json={"gym_name": "Gym One", "owner_name": "Owner 1", "email": "g1@test.com", "password": "Pass@1"},
    )
    headers_1 = {"Authorization": f"Bearer {reg_1.json()['access_token']}"}

    # Register Gym 2
    reg_2 = await client.post(
        "/api/v1/auth/register",
        json={"gym_name": "Gym Two", "owner_name": "Owner 2", "email": "g2@test.com", "password": "Pass@2"},
    )
    headers_2 = {"Authorization": f"Bearer {reg_2.json()['access_token']}"}

    # Gym 1 adds 2 members
    await client.post("/api/v1/members", headers=headers_1, json={"name": "M1", "email": "m1@g1.com", "phone": "+91 91111 11111"})
    await client.post("/api/v1/members", headers=headers_1, json={"name": "M2", "email": "m2@g1.com", "phone": "+91 91111 22222"})

    # Gym 2 adds 1 member
    await client.post("/api/v1/members", headers=headers_2, json={"name": "M3", "email": "m3@g2.com", "phone": "+91 92222 11111"})

    # Check Gym 1 Overview
    o1 = await client.get("/api/v1/analytics/overview", headers=headers_1)
    assert o1.json()["total_members"]["value"] == 2.0

    # Check Gym 2 Overview
    o2 = await client.get("/api/v1/analytics/overview", headers=headers_2)
    assert o2.json()["total_members"]["value"] == 1.0

    # Gym 2 adds a trainer
    await client.post("/api/v1/trainers", headers=headers_2, json={"name": "Coach Two", "email": "c2@g2.com", "specialty": "HIIT"})

    # Verify Gym 1 has 0 trainers
    t1 = await client.get("/api/v1/analytics/trainers", headers=headers_1)
    assert t1.json()["total_trainers"] == 0

    # Verify Gym 2 has 1 trainer
    t2 = await client.get("/api/v1/analytics/trainers", headers=headers_2)
    assert t2.json()["total_trainers"] == 1
