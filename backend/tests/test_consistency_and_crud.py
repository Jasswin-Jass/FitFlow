import pytest
import uuid
from datetime import date
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_new_gym_receives_default_membership_plans(client: AsyncClient):
    # 1. Register a new gym
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Zenith Fitness Club",
            "owner_name": "Zenith Owner",
            "email": "owner@zenithfitness.com",
            "password": "ZenithPassword123!",
        },
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify default plans were automatically provisioned
    plans_resp = await client.get("/api/v1/membership-plans", headers=headers)
    assert plans_resp.status_code == 200
    plans = plans_resp.json()["items"]
    assert len(plans) == 3

    plan_names = {p["name"] for p in plans}
    assert "Power Monthly" in plan_names
    assert "Power Quarterly" in plan_names
    assert "Premium Annual" in plan_names

    for p in plans:
        assert p["status"] == "active"
        assert p["description"] is not None
        assert p["price"] > 0
        assert p["duration_days"] > 0

    # 3. Create a custom plan
    new_plan_resp = await client.post(
        "/api/v1/membership-plans",
        headers=headers,
        json={
            "name": "Weekend Warrior",
            "description": "Access exclusively on Saturday and Sunday",
            "price": 999.0,
            "duration_days": 30,
            "status": "active",
        },
    )
    assert new_plan_resp.status_code == 201
    custom_plan = new_plan_resp.json()
    assert custom_plan["name"] == "Weekend Warrior"
    assert custom_plan["status"] == "active"

    # 4. Update the custom plan
    patch_resp = await client.patch(
        f"/api/v1/membership-plans/{custom_plan['id']}",
        headers=headers,
        json={"status": "inactive", "price": 1099.0},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "inactive"
    assert patch_resp.json()["price"] == 1099.0


@pytest.mark.asyncio
async def test_member_demographics_crud_and_age(client: AsyncClient):
    # 1. Register Gym
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Apex Athletics",
            "owner_name": "Apex Owner",
            "email": "owner@apexathletics.com",
            "password": "ApexPassword123!",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add Member with DOB and rich demographics
    mem_resp = await client.post(
        "/api/v1/members",
        headers=headers,
        json={
            "name": "Swetha Krishnan",
            "first_name": "Swetha",
            "last_name": "Krishnan",
            "email": "swetha@apexathletics.com",
            "phone": "+91 98401 55667",
            "date_of_birth": "1996-03-15",
            "gender": "Female",
            "occupation": "Architect",
            "city": "Chennai",
            "fitness_goal": "Endurance",
            "preferred_training_time": "Morning",
            "acquisition_source": "Social Media",
            "status": "active",
        },
    )
    assert mem_resp.status_code == 201
    member = mem_resp.json()
    member_id = member["id"]

    # Verify dynamic age calculation (DOB: 1996)
    expected_age = date.today().year - 1996 - (
        (date.today().month, date.today().day) < (3, 15)
    )
    assert member["age"] == expected_age
    assert member["gender"] == "Female"
    assert member["occupation"] == "Architect"
    assert member["city"] == "Chennai"

    # 3. Edit Member demographics
    edit_resp = await client.patch(
        f"/api/v1/members/{member_id}",
        headers=headers,
        json={
            "occupation": "Senior Architect",
            "city": "Bengaluru",
            "fitness_goal": "Athletic",
        },
    )
    assert edit_resp.status_code == 200
    updated = edit_resp.json()
    assert updated["occupation"] == "Senior Architect"
    assert updated["city"] == "Bengaluru"
    assert updated["fitness_goal"] == "Athletic"
    assert updated["age"] == expected_age


@pytest.mark.asyncio
async def test_trainer_workload_assignments_and_reviews(client: AsyncClient):
    # 1. Register Gym
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Pulse Performance",
            "owner_name": "Pulse Owner",
            "email": "owner@pulseperformance.com",
            "password": "PulsePassword123!",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Trainer with experience and capacity
    t_resp = await client.post(
        "/api/v1/trainers",
        headers=headers,
        json={
            "name": "Coach Vikram",
            "email": "vikram@pulseperformance.com",
            "phone": "+91 99999 11111",
            "specialty": "Strength & Conditioning",
            "years_of_experience": 6,
            "max_client_capacity": 10,
            "bio": "Certified strength coach specializing in Olympic lifting.",
        },
    )
    assert t_resp.status_code == 201
    trainer = t_resp.json()
    trainer_id = trainer["id"]
    assert trainer["rating"] is None  # Not rated yet
    assert trainer["review_count"] == 0
    assert trainer["assigned_clients_count"] == 0
    assert trainer["client_load_percent"] == 0.0

    # 3. Create Member
    m_resp = await client.post(
        "/api/v1/members",
        headers=headers,
        json={
            "name": "Naveen Raj",
            "email": "naveen@pulseperformance.com",
            "phone": "+91 99999 22222",
            "gender": "Male",
            "date_of_birth": "1992-08-25",
        },
    )
    assert m_resp.status_code == 201
    member_id = m_resp.json()["id"]

    # 4. Assign Member to Trainer
    assign_resp = await client.post(
        f"/api/v1/trainers/{trainer_id}/clients",
        headers=headers,
        json={"member_id": member_id},
    )
    assert assign_resp.status_code == 201
    assert assign_resp.json()["member_id"] == member_id

    # Verify trainer workload reflects assignment
    t_refreshed = await client.get(f"/api/v1/trainers/{trainer_id}", headers=headers)
    assert t_refreshed.status_code == 200
    assert t_refreshed.json()["assigned_clients_count"] == 1
    assert t_refreshed.json()["client_load_percent"] == 10.0  # 1/10 * 100%

    # Verify list of clients
    clients_resp = await client.get(f"/api/v1/trainers/{trainer_id}/clients", headers=headers)
    assert clients_resp.status_code == 200
    assert len(clients_resp.json()["items"]) == 1
    assert clients_resp.json()["items"][0]["name"] == "Naveen Raj"

    # 5. Add Review 1: Rating 5
    rev1 = await client.post(
        f"/api/v1/trainers/{trainer_id}/reviews",
        headers=headers,
        json={
            "member_id": member_id,
            "rating": 5,
            "review": "Best strength trainer I have worked with!",
        },
    )
    assert rev1.status_code == 201

    # Check updated trainer rating: 5.0 (1 review)
    t_rev1 = await client.get(f"/api/v1/trainers/{trainer_id}", headers=headers)
    assert t_rev1.json()["rating"] == 5.0
    assert t_rev1.json()["review_count"] == 1

    # Add Review 2: Rating 4
    rev2 = await client.post(
        f"/api/v1/trainers/{trainer_id}/reviews",
        headers=headers,
        json={
            "member_id": member_id,
            "rating": 4,
            "review": "Very focused and energetic coach.",
        },
    )
    assert rev2.status_code == 201

    # Check updated trainer rating: 4.5 ((5+4)/2)
    t_rev2 = await client.get(f"/api/v1/trainers/{trainer_id}", headers=headers)
    assert t_rev2.json()["rating"] == 4.5
    assert t_rev2.json()["review_count"] == 2

    # 6. Unassign Member
    unassign_resp = await client.delete(
        f"/api/v1/trainers/{trainer_id}/clients/{member_id}",
        headers=headers,
    )
    assert unassign_resp.status_code == 204

    # Verify workload drops to 0
    t_unassigned = await client.get(f"/api/v1/trainers/{trainer_id}", headers=headers)
    assert t_unassigned.json()["assigned_clients_count"] == 0
    assert t_unassigned.json()["client_load_percent"] == 0.0


@pytest.mark.asyncio
async def test_strict_tenant_isolation_plans_and_trainers(client: AsyncClient):
    # Register Gym 1
    reg1 = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Tenant One Gym",
            "owner_name": "T1 Owner",
            "email": "t1@gym.com",
            "password": "Password123!",
        },
    )
    t1_token = reg1.json()["access_token"]
    t1_headers = {"Authorization": f"Bearer {t1_token}"}

    # Register Gym 2
    reg2 = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Tenant Two Gym",
            "owner_name": "T2 Owner",
            "email": "t2@gym.com",
            "password": "Password123!",
        },
    )
    t2_token = reg2.json()["access_token"]
    t2_headers = {"Authorization": f"Bearer {t2_token}"}

    # Gym 1 gets its plans
    t1_plans = (await client.get("/api/v1/membership-plans", headers=t1_headers)).json()["items"]
    t1_plan_id = t1_plans[0]["id"]

    # Gym 2 gets its plans
    t2_plans = (await client.get("/api/v1/membership-plans", headers=t2_headers)).json()["items"]
    t2_plan_id = t2_plans[0]["id"]

    # Gym 1 cannot view Gym 2's plan
    cross_plan = await client.get(f"/api/v1/membership-plans/{t2_plan_id}", headers=t1_headers)
    assert cross_plan.status_code in (403, 404)

    # Gym 2 cannot view Gym 1's plan
    cross_plan2 = await client.get(f"/api/v1/membership-plans/{t1_plan_id}", headers=t2_headers)
    assert cross_plan2.status_code in (403, 404)

    # Gym 1 creates trainer
    t1_tr = (await client.post(
        "/api/v1/trainers",
        headers=t1_headers,
        json={"name": "T1 Coach", "email": "coach@t1.com", "specialty": "HIIT"},
    )).json()

    # Gym 2 creates member
    t2_mem = (await client.post(
        "/api/v1/members",
        headers=t2_headers,
        json={"name": "T2 Member", "email": "mem@t2.com", "phone": "+91 99999 33333"},
    )).json()

    # Cross-tenant assignment attempt must fail
    cross_assign = await client.post(
        f"/api/v1/trainers/{t1_tr['id']}/clients",
        headers=t1_headers,
        json={"member_id": t2_mem["id"]},
    )
    assert cross_assign.status_code in (403, 404)
