import uuid
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.payment_reminder import PaymentReminder
from app.models.payment_subscription import PaymentSubscription
from app.models.membership import Membership
from app.models.member import Member
from app.models.membership_plan import MembershipPlan
from app.schemas.payment import (
    AutomationStatusResponse,
    PaymentReminderResponse,
)


AUTOMATION_RULES = [
    {
        "id": "expiry_7d",
        "name": "7 Days Before Expiration",
        "description": "Sends a friendly renewal reminder 7 days before membership expires",
        "enabled": True,
        "channels": ["In-App Notification", "Email (Staged)", "WhatsApp (Staged)"],
    },
    {
        "id": "expiry_2d",
        "name": "48 Hours Urgency Alert",
        "description": "Urgent renewal prompt 2 days prior to membership termination",
        "enabled": True,
        "channels": ["In-App Notification", "SMS (Staged)"],
    },
    {
        "id": "expiry_today",
        "name": "Expiration Day Notice",
        "description": "Final reminder on the exact day membership expires",
        "enabled": True,
        "channels": ["In-App Notification"],
    },
    {
        "id": "payment_failed",
        "name": "Failed Payment & Retry Alert",
        "description": "Immediate incident alert with retry link when payment or auto-debit fails",
        "enabled": True,
        "channels": ["In-App Notification", "SMS (Staged)"],
    },
]


async def generate_due_reminders(session: AsyncSession, gym_id: uuid.UUID) -> int:
    """
    Evaluates membership expiration windows and generates in-app reminders idempotently.
    """
    today = date.today()
    in_7d = today + timedelta(days=7)
    in_2d = today + timedelta(days=2)

    # 1. Check 7-day window
    m7_res = await session.execute(
        select(Membership, Member, MembershipPlan)
        .join(Member, Membership.member_id == Member.id)
        .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.end_date == in_7d,
        )
    )
    created_count = 0
    for mship, mem, plan in m7_res.all():
        # Check idempotency
        existing = await session.execute(
            select(PaymentReminder.id).where(
                PaymentReminder.gym_id == gym_id,
                PaymentReminder.member_id == mem.id,
                PaymentReminder.reminder_type == "expiry_7d",
                PaymentReminder.created_at >= datetime.combine(today - timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc),
            )
        )
        if not existing.scalar():
            rem = PaymentReminder(
                gym_id=gym_id,
                member_id=mem.id,
                reminder_type="expiry_7d",
                title="Membership Renewal Upcoming (7 Days)",
                message=f"Hi {mem.name}, your {plan.name} membership expires in 7 days ({mship.end_date}). Renew now to maintain gym access.",
                channel="in_app",
                status="sent",
            )
            session.add(rem)
            created_count += 1

    # 2. Check 2-day window
    m2_res = await session.execute(
        select(Membership, Member, MembershipPlan)
        .join(Member, Membership.member_id == Member.id)
        .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.end_date == in_2d,
        )
    )
    for mship, mem, plan in m2_res.all():
        existing = await session.execute(
            select(PaymentReminder.id).where(
                PaymentReminder.gym_id == gym_id,
                PaymentReminder.member_id == mem.id,
                PaymentReminder.reminder_type == "expiry_2d",
                PaymentReminder.created_at >= datetime.combine(today - timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc),
            )
        )
        if not existing.scalar():
            rem = PaymentReminder(
                gym_id=gym_id,
                member_id=mem.id,
                reminder_type="expiry_2d",
                title="Membership Expires in 48 Hours",
                message=f"Important: Your {plan.name} expires on {mship.end_date}. Tap Pay Now to renew without interruption.",
                channel="in_app",
                status="sent",
            )
            session.add(rem)
            created_count += 1

    if created_count > 0:
        await session.commit()

    return created_count


async def get_automation_status(
    session: AsyncSession, gym_id: uuid.UUID
) -> AutomationStatusResponse:
    # Trigger reminder check
    await generate_due_reminders(session, gym_id)

    today = date.today()

    # Active subscriptions
    active_subs_res = await session.execute(
        select(func.count(PaymentSubscription.id)).where(
            PaymentSubscription.gym_id == gym_id,
            PaymentSubscription.status == "active",
        )
    )
    active_subs = active_subs_res.scalar() or 0

    # Due subscriptions
    due_subs_res = await session.execute(
        select(func.count(PaymentSubscription.id)).where(
            PaymentSubscription.gym_id == gym_id,
            PaymentSubscription.status == "active",
            PaymentSubscription.next_billing_date <= today,
        )
    )
    due_subs = due_subs_res.scalar() or 0

    # Recent reminders
    rem_res = await session.execute(
        select(PaymentReminder, Member.name.label("member_name"))
        .join(Member, PaymentReminder.member_id == Member.id)
        .where(PaymentReminder.gym_id == gym_id)
        .order_by(desc(PaymentReminder.created_at))
        .limit(20)
    )
    rem_rows = rem_res.all()

    recent_reminders = [
        PaymentReminderResponse(
            id=rem.id,
            gym_id=rem.gym_id,
            member_id=rem.member_id,
            member_name=mem_name,
            payment_id=rem.payment_id,
            reminder_type=rem.reminder_type,
            title=rem.title,
            message=rem.message,
            channel=rem.channel,
            status=rem.status,
            created_at=rem.created_at,
        )
        for rem, mem_name in rem_rows
    ]

    return AutomationStatusResponse(
        provider="Demo Payment Provider",
        reminders_enabled=True,
        rules=AUTOMATION_RULES,
        active_subscriptions_count=active_subs,
        due_subscriptions_count=due_subs,
        recent_reminders=recent_reminders,
    )


async def list_reminders(
    session: AsyncSession, gym_id: uuid.UUID, limit: int = 50
) -> List[PaymentReminderResponse]:
    rem_res = await session.execute(
        select(PaymentReminder, Member.name.label("member_name"))
        .join(Member, PaymentReminder.member_id == Member.id)
        .where(PaymentReminder.gym_id == gym_id)
        .order_by(desc(PaymentReminder.created_at))
        .limit(limit)
    )
    return [
        PaymentReminderResponse(
            id=rem.id,
            gym_id=rem.gym_id,
            member_id=rem.member_id,
            member_name=mem_name,
            payment_id=rem.payment_id,
            reminder_type=rem.reminder_type,
            title=rem.title,
            message=rem.message,
            channel=rem.channel,
            status=rem.status,
            created_at=rem.created_at,
        )
        for rem, mem_name in rem_res.all()
    ]
