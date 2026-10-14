import pytest
import uuid
from datetime import date, datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.gym import Gym
from app.models.user import User
from app.models.member import Member
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.models.payment import Payment
from app.models.payment_subscription import PaymentSubscription
from app.core.security import create_access_token, get_password_hash


@pytest.mark.asyncio
async def test_create_and_lifecycle_payment(client: AsyncClient, db_session: AsyncSession):
    # Setup Gym and Owner
    gym = Gym(name="Test Payment Gym")
    db_session.add(gym)
    await db_session.flush()

    user = User(
        gym_id=gym.id,
        email="owner@testpaymentgym.com",
        hashed_password=get_password_hash("Password@123"),
        role="owner",
    )
    db_session.add(user)

    plan = MembershipPlan(
        gym_id=gym.id,
        name="Monthly Test",
        price=1800.0,
        duration_days=30,
        status="active",
    )
    db_session.add(plan)

    member = Member(
        gym_id=gym.id,
        name="Vikram Raman",
        email="vikram.r@gmail.com",
        phone="+91 98401 11223",
        join_date=date.today(),
        status="active",
    )
    db_session.add(member)
    await db_session.flush()

    membership = Membership(
        gym_id=gym.id,
        member_id=member.id,
        plan_id=plan.id,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        status="active",
    )
    db_session.add(membership)
    await db_session.commit()

    token = create_access_token(subject=str(user.id), gym_id=str(gym.id), role=user.role, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Payment
    resp = await client.post(
        "/api/v1/payments/create",
        json={
            "member_id": str(member.id),
            "membership_id": str(membership.id),
            "amount": 1800.0,
            "payment_method": "upi",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    pay_data = resp.json()
    payment_id = pay_data["id"]
    assert pay_data["status"] == "pending"
    assert pay_data["amount"] == 1800.0
    assert pay_data["provider"] == "demo"
    assert pay_data["provider_payment_id"].startswith("pay_demo_")

    # 2. Cancel Payment
    cancel_resp = await client.post(f"/api/v1/payments/{payment_id}/cancel", headers=headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    # 3. Retry Payment
    retry_resp = await client.post(f"/api/v1/payments/{payment_id}/retry", headers=headers)
    assert retry_resp.status_code == 200
    assert retry_resp.json()["status"] == "pending"

    # 4. Simulate Failure
    fail_resp = await client.post(
        f"/api/v1/payments/{payment_id}/simulate-failure",
        json={"failure_reason": "UPI Pin entered was incorrect"},
        headers=headers,
    )
    assert fail_resp.status_code == 200
    fail_data = fail_resp.json()
    assert fail_data["status"] == "failed"
    assert fail_data["failure_reason"] == "UPI Pin entered was incorrect"

    # 5. Retry and Simulate Success
    await client.post(f"/api/v1/payments/{payment_id}/retry", headers=headers)
    succ_resp = await client.post(f"/api/v1/payments/{payment_id}/simulate-success", headers=headers)
    assert succ_resp.status_code == 200
    succ_data = succ_resp.json()
    assert succ_data["status"] == "paid"
    assert succ_data["paid_at"] is not None
    assert succ_data["failure_reason"] is None


@pytest.mark.asyncio
async def test_auto_renewal_mandates_and_simulations(client: AsyncClient, db_session: AsyncSession):
    gym = Gym(name="Auto Renewal Gym")
    db_session.add(gym)
    await db_session.flush()

    user = User(
        gym_id=gym.id,
        email="owner@autorenewalgym.com",
        hashed_password=get_password_hash("Password@123"),
        role="owner",
    )
    db_session.add(user)

    plan = MembershipPlan(
        gym_id=gym.id,
        name="Quarterly Fit",
        price=4500.0,
        duration_days=90,
        status="active",
    )
    db_session.add(plan)

    member = Member(
        gym_id=gym.id,
        name="Priya Natarajan",
        email="priya.n@gmail.com",
        phone="+91 98402 33445",
        join_date=date.today(),
        status="active",
    )
    db_session.add(member)
    await db_session.flush()

    old_end = date.today() + timedelta(days=90)
    membership = Membership(
        gym_id=gym.id,
        member_id=member.id,
        plan_id=plan.id,
        start_date=date.today(),
        end_date=old_end,
        status="active",
    )
    db_session.add(membership)
    await db_session.commit()

    token = create_access_token(subject=str(user.id), gym_id=str(gym.id), role=user.role, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Enable Auto Renewal
    resp = await client.post(
        "/api/v1/payments/auto-renewal",
        json={"member_id": str(member.id), "membership_id": str(membership.id)},
        headers=headers,
    )
    assert resp.status_code == 201
    sub_data = resp.json()
    subscription_id = sub_data["id"]
    assert sub_data["status"] == "active"
    assert sub_data["amount"] == 4500.0
    assert sub_data["billing_interval"] == "quarterly"
    assert sub_data["next_billing_date"] == str(old_end)

    # 2. Get member subscription
    get_sub_resp = await client.get(f"/api/v1/payments/auto-renewal/{member.id}", headers=headers)
    assert get_sub_resp.status_code == 200
    assert get_sub_resp.json()["id"] == subscription_id

    # 3. Simulate Successful Renewal
    succ_renew = await client.post(
        f"/api/v1/payments/auto-renewal/{subscription_id}/simulate-success", headers=headers
    )
    assert succ_renew.status_code == 200
    renewed_data = succ_renew.json()
    assert renewed_data["status"] == "active"
    expected_new_end = old_end + timedelta(days=90)
    assert renewed_data["next_billing_date"] == str(expected_new_end)

    # Check database: membership was extended and payment record exists
    await db_session.refresh(membership)
    assert membership.end_date == expected_new_end

    # Check payment created
    pay_check = await db_session.execute(
        select(Payment).where(Payment.membership_id == membership.id, Payment.status == "paid")
    )
    assert len(pay_check.scalars().all()) >= 1

    # 4. Simulate Failed Renewal
    fail_renew = await client.post(
        f"/api/v1/payments/auto-renewal/{subscription_id}/simulate-failure",
        json={"failure_reason": "Insufficient balance in account"},
        headers=headers,
    )
    assert fail_renew.status_code == 200
    assert fail_renew.json()["status"] == "past_due"

    # Membership must NOT be extended further!
    await db_session.refresh(membership)
    assert membership.end_date == expected_new_end

    # 5. Cancel Auto Renewal
    cancel_resp = await client.post(
        f"/api/v1/payments/auto-renewal/{subscription_id}/cancel", headers=headers
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_process_due_payments_and_idempotency(client: AsyncClient, db_session: AsyncSession):
    gym = Gym(name="Batch Due Gym")
    db_session.add(gym)
    await db_session.flush()

    user = User(
        gym_id=gym.id,
        email="owner@batchduegym.com",
        hashed_password=get_password_hash("Password@123"),
        role="owner",
    )
    db_session.add(user)

    plan = MembershipPlan(
        gym_id=gym.id,
        name="Power 30",
        price=2000.0,
        duration_days=30,
        status="active",
    )
    db_session.add(plan)

    member = Member(
        gym_id=gym.id,
        name="Anand Sundaram",
        email="anand.s@gmail.com",
        phone="+91 98403 44556",
        join_date=date.today() - timedelta(days=60),
        status="active",
    )
    db_session.add(member)
    await db_session.flush()

    # Membership expiring TODAY
    today = date.today()
    membership = Membership(
        gym_id=gym.id,
        member_id=member.id,
        plan_id=plan.id,
        start_date=today - timedelta(days=30),
        end_date=today,
        status="active",
    )
    db_session.add(membership)
    await db_session.flush()

    # Active subscription with next_billing_date = today (DUE NOW!)
    sub = PaymentSubscription(
        gym_id=gym.id,
        member_id=member.id,
        membership_id=membership.id,
        provider="demo",
        provider_subscription_id="sub_demo_batchtest",
        amount=2000.0,
        currency="INR",
        billing_interval="monthly",
        status="active",
        start_date=today - timedelta(days=30),
        next_billing_date=today,
    )
    db_session.add(sub)
    await db_session.commit()

    token = create_access_token(subject=str(user.id), gym_id=str(gym.id), role=user.role, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    # Run batch runner: POST /admin/process-due-payments
    batch_resp = await client.post("/api/v1/admin/process-due-payments", headers=headers)
    assert batch_resp.status_code == 200
    res_data = batch_resp.json()
    assert res_data["processed"] == 1
    assert res_data["succeeded"] == 1
    assert res_data["total_collected"] == 2000.0

    # Verify membership extended by 30 days
    await db_session.refresh(membership)
    assert membership.end_date == today + timedelta(days=30)

    # Verify subscription next_billing_date advanced
    await db_session.refresh(sub)
    assert sub.next_billing_date == today + timedelta(days=30)

    # IDEMPOTENCY TEST: Run batch runner a SECOND time immediately!
    batch_resp_2 = await client.post("/api/v1/admin/process-due-payments", headers=headers)
    assert batch_resp_2.status_code == 200
    # Next billing date is already in future, so 0 due processed
    assert batch_resp_2.json()["processed"] == 0

    # Verify total payments created is exactly 1 (no duplicates!)
    pay_count = await db_session.execute(
        select(func.count(Payment.id)).where(Payment.membership_id == membership.id)
    )
    assert pay_count.scalar() == 1


@pytest.mark.asyncio
async def test_tenant_isolation_payments_and_mandates(client: AsyncClient, db_session: AsyncSession):
    # Gym A
    gym_a = Gym(name="Gym Alpha Payments")
    db_session.add(gym_a)
    await db_session.flush()

    user_a = User(
        gym_id=gym_a.id,
        email="owner@payisolation-a.com",
        hashed_password=get_password_hash("Password@123"),
        role="owner",
    )
    member_a = Member(
        gym_id=gym_a.id,
        name="Member Alpha",
        email="alpha@gmail.com",
        phone="+91 99999 11111",
        join_date=date.today(),
        status="active",
    )
    db_session.add_all([user_a, member_a])
    await db_session.flush()

    pay_a = Payment(
        gym_id=gym_a.id,
        member_id=member_a.id,
        amount=1500.0,
        currency="INR",
        status="pending",
        provider="demo",
    )
    db_session.add(pay_a)

    # Gym B
    gym_b = Gym(name="Gym Beta Payments")
    db_session.add(gym_b)
    await db_session.flush()

    user_b = User(
        gym_id=gym_b.id,
        email="owner@payisolation-b.com",
        hashed_password=get_password_hash("Password@123"),
        role="owner",
    )
    member_b = Member(
        gym_id=gym_b.id,
        name="Member Beta",
        email="beta@gmail.com",
        phone="+91 99999 22222",
        join_date=date.today(),
        status="active",
    )
    db_session.add_all([user_b, member_b])
    await db_session.flush()

    pay_b = Payment(
        gym_id=gym_b.id,
        member_id=member_b.id,
        amount=3000.0,
        currency="INR",
        status="pending",
        provider="demo",
    )
    db_session.add(pay_b)
    await db_session.commit()

    token_b = create_access_token(subject=str(user_b.id), gym_id=str(gym_b.id), role=user_b.role, email=user_b.email)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Gym B tries to read Gym A's payment details
    get_res = await client.get(f"/api/v1/payments/{pay_a.id}", headers=headers_b)
    assert get_res.status_code == 404

    # 2. Gym B tries to simulate success on Gym A's payment
    sim_res = await client.post(f"/api/v1/payments/{pay_a.id}/simulate-success", headers=headers_b)
    assert sim_res.status_code == 404

    # 3. Gym B lists payments: must NOT see Gym A's payment
    list_res = await client.get("/api/v1/payments", headers=headers_b)
    assert list_res.status_code == 200
    ids = [item["id"] for item in list_res.json()["items"]]
    assert str(pay_b.id) in ids
    assert str(pay_a.id) not in ids


@pytest.mark.asyncio
async def test_webhook_idempotency(client: AsyncClient, db_session: AsyncSession):
    # Send a webhook event
    payload = {
        "event_id": "evt_unique_12345",
        "event": "payment.captured",
        "payload": {"payment_id": "pay_demo_test", "amount": 1500},
    }
    resp1 = await client.post("/api/v1/webhooks/payment?provider=demo", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "processed"

    # Send the exact same event ID again
    resp2 = await client.post("/api/v1/webhooks/payment?provider=demo", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "duplicate"


@pytest.mark.asyncio
async def test_automation_status_and_reminders(client: AsyncClient, db_session: AsyncSession):
    gym = Gym(name="Reminders Gym")
    db_session.add(gym)
    await db_session.flush()

    user = User(
        gym_id=gym.id,
        email="owner@remindersgym.com",
        hashed_password=get_password_hash("Password@123"),
        role="owner",
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(subject=str(user.id), gym_id=str(gym.id), role=user.role, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    status_resp = await client.get("/api/v1/automation/status", headers=headers)
    assert status_resp.status_code == 200
    s_data = status_resp.json()
    assert s_data["provider"] == "Demo Payment Provider"
    assert s_data["reminders_enabled"] is True
    assert len(s_data["rules"]) >= 4

    reminders_resp = await client.get("/api/v1/automation/reminders", headers=headers)
    assert reminders_resp.status_code == 200
    assert isinstance(reminders_resp.json(), list)
