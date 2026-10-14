import uuid
from datetime import datetime, date, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_

from app.models.payment import Payment
from app.models.payment_subscription import PaymentSubscription
from app.models.payment_webhook_event import PaymentWebhookEvent
from app.models.payment_reminder import PaymentReminder
from app.models.member import Member
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentListResponse,
    PaymentSubscriptionResponse,
    DuePaymentsProcessResponse,
)
from app.payments import get_payment_provider
from app.core.exceptions import ResourceNotFoundException, TenantAccessDeniedException, FitFlowException
from app.analytics.aggregation_service import compute_and_save_daily_metrics


async def list_payments(
    session: AsyncSession,
    gym_id: uuid.UUID,
    status: Optional[str] = None,
    member_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    size: int = 20,
) -> PaymentListResponse:
    query = (
        select(Payment, Member, MembershipPlan.name.label("plan_name"))
        .join(Member, Payment.member_id == Member.id)
        .outerjoin(Membership, Payment.membership_id == Membership.id)
        .outerjoin(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(Payment.gym_id == gym_id)
    )

    if status and status != "all":
        # Handle 'success' as alias for 'paid'
        if status in ("success", "paid"):
            query = query.where(Payment.status.in_(("success", "paid")))
        else:
            query = query.where(Payment.status == status)

    if member_id:
        query = query.where(Payment.member_id == member_id)

    if start_date:
        start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        query = query.where(or_(Payment.paid_at >= start_dt, Payment.created_at >= start_dt))

    if end_date:
        end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = query.where(or_(Payment.paid_at <= end_dt, Payment.created_at <= end_dt))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await session.execute(count_query)
    total = total_res.scalar() or 0

    offset = (page - 1) * size
    query = query.order_by(desc(Payment.created_at)).offset(offset).limit(size)
    res = await session.execute(query)
    rows = res.all()

    # Check recurring subscriptions
    member_ids = [mem.id for _, mem, _ in rows]
    sub_map: Dict[uuid.UUID, bool] = {}
    if member_ids:
        subs_res = await session.execute(
            select(PaymentSubscription.member_id).where(
                PaymentSubscription.gym_id == gym_id,
                PaymentSubscription.member_id.in_(member_ids),
                PaymentSubscription.status == "active",
            )
        )
        for s_mid in subs_res.scalars().all():
            sub_map[s_mid] = True

    items = [
        PaymentResponse(
            id=pmt.id,
            gym_id=pmt.gym_id,
            member_id=pmt.member_id,
            member_name=mem.name,
            member_email=mem.email,
            membership_id=pmt.membership_id,
            plan_name=plan_name,
            amount=float(pmt.amount),
            currency=pmt.currency or "INR",
            status="paid" if pmt.status == "success" else pmt.status,
            payment_method=pmt.payment_method or "upi",
            provider=pmt.provider or "demo",
            provider_payment_id=pmt.provider_payment_id,
            payment_link_id=pmt.payment_link_id,
            due_date=pmt.due_date,
            paid_at=pmt.paid_at,
            failure_reason=pmt.failure_reason,
            is_recurring=sub_map.get(pmt.member_id, False),
            created_at=pmt.created_at,
            updated_at=pmt.updated_at,
        )
        for pmt, mem, plan_name in rows
    ]
    pages = (total + size - 1) // size if total > 0 else 1

    return PaymentListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


async def get_payment(
    session: AsyncSession, gym_id: uuid.UUID, payment_id: uuid.UUID
) -> PaymentResponse:
    query = (
        select(Payment, Member, MembershipPlan.name.label("plan_name"))
        .join(Member, Payment.member_id == Member.id)
        .outerjoin(Membership, Payment.membership_id == Membership.id)
        .outerjoin(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(Payment.id == payment_id, Payment.gym_id == gym_id)
    )
    res = await session.execute(query)
    row = res.first()
    if not row:
        raise ResourceNotFoundException("Payment", payment_id)

    pmt, mem, plan_name = row
    sub_res = await session.execute(
        select(PaymentSubscription.id).where(
            PaymentSubscription.gym_id == gym_id,
            PaymentSubscription.member_id == pmt.member_id,
            PaymentSubscription.status == "active",
        )
    )
    is_recurring = sub_res.scalar() is not None

    return PaymentResponse(
        id=pmt.id,
        gym_id=pmt.gym_id,
        member_id=pmt.member_id,
        member_name=mem.name,
        member_email=mem.email,
        membership_id=pmt.membership_id,
        plan_name=plan_name,
        amount=float(pmt.amount),
        currency=pmt.currency or "INR",
        status="paid" if pmt.status == "success" else pmt.status,
        payment_method=pmt.payment_method or "upi",
        provider=pmt.provider or "demo",
        provider_payment_id=pmt.provider_payment_id,
        payment_link_id=pmt.payment_link_id,
        due_date=pmt.due_date,
        paid_at=pmt.paid_at,
        failure_reason=pmt.failure_reason,
        is_recurring=is_recurring,
        created_at=pmt.created_at,
        updated_at=pmt.updated_at,
    )


async def create_payment(
    session: AsyncSession, gym_id: uuid.UUID, data: PaymentCreate
) -> PaymentResponse:
    member = await session.get(Member, data.member_id)
    if not member or member.gym_id != gym_id:
        raise ResourceNotFoundException("Member", data.member_id)

    plan_name = None
    membership = None
    if data.membership_id:
        membership = await session.get(Membership, data.membership_id)
        if not membership or membership.gym_id != gym_id:
            raise ResourceNotFoundException("Membership", data.membership_id)
        plan = await session.get(MembershipPlan, membership.plan_id)
        plan_name = plan.name if plan else None
    else:
        # Check if member has active membership
        m_res = await session.execute(
            select(Membership, MembershipPlan.name.label("p_name"))
            .outerjoin(MembershipPlan, Membership.plan_id == MembershipPlan.id)
            .where(Membership.gym_id == gym_id, Membership.member_id == member.id)
            .order_by(desc(Membership.end_date))
        )
        first_m = m_res.first()
        if first_m:
            membership, plan_name = first_m[0], first_m[1]

    provider = get_payment_provider("demo")
    provider_res = await provider.create_payment(
        amount=data.amount,
        currency=data.currency,
        member_id=member.id,
        membership_id=membership.id if membership else None,
        payment_method=data.payment_method or "upi",
    )

    init_status = data.status if data.status in ("pending", "processing", "paid", "failed") else "pending"
    paid_dt = data.paid_at if init_status == "paid" else None

    payment = Payment(
        gym_id=gym_id,
        member_id=member.id,
        membership_id=membership.id if membership else None,
        amount=data.amount,
        currency=data.currency,
        status=init_status,
        payment_method=data.payment_method or "upi",
        provider=provider.provider_name,
        provider_payment_id=provider_res.provider_payment_id,
        payment_link_id=provider_res.payment_link,
        due_date=data.due_date or date.today(),
        paid_at=paid_dt,
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)

    return PaymentResponse(
        id=payment.id,
        gym_id=payment.gym_id,
        member_id=payment.member_id,
        member_name=member.name,
        member_email=member.email,
        membership_id=payment.membership_id,
        plan_name=plan_name,
        amount=float(payment.amount),
        currency=payment.currency,
        status=payment.status,
        payment_method=payment.payment_method,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        payment_link_id=payment.payment_link_id,
        due_date=payment.due_date,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


async def simulate_payment_success(
    session: AsyncSession, gym_id: uuid.UUID, payment_id: uuid.UUID
) -> PaymentResponse:
    payment = await session.get(Payment, payment_id)
    if not payment or payment.gym_id != gym_id:
        raise ResourceNotFoundException("Payment", payment_id)

    now = datetime.now(timezone.utc)
    payment.status = "paid"
    payment.paid_at = now
    payment.failure_reason = None

    member = await session.get(Member, payment.member_id)
    if member:
        member.status = "active"

    # If linked to membership, extend or activate it
    plan_name = None
    if payment.membership_id:
        membership = await session.get(Membership, payment.membership_id)
        if membership:
            plan = await session.get(MembershipPlan, membership.plan_id)
            if plan:
                plan_name = plan.name
                today = date.today()
                # If membership is expired or about to expire, extend from current end or today
                if membership.end_date <= today:
                    membership.start_date = today
                    membership.end_date = today + timedelta(days=plan.duration_days)
                elif membership.end_date <= today + timedelta(days=7):
                    membership.end_date = membership.end_date + timedelta(days=plan.duration_days)
                membership.status = "active"

    # Add reminder log
    reminder = PaymentReminder(
        gym_id=gym_id,
        member_id=payment.member_id,
        payment_id=payment.id,
        reminder_type="renewal_success",
        title="Payment Verified & Receipt Generated",
        message=f"Payment of ₹{float(payment.amount):,.0f} was successfully completed via {payment.payment_method or 'UPI'}.",
        channel="in_app",
        status="sent",
    )
    session.add(reminder)

    await session.commit()
    await session.refresh(payment)

    # Recompute daily metrics
    await compute_and_save_daily_metrics(session, gym_id=gym_id, metric_date=date.today())

    return PaymentResponse(
        id=payment.id,
        gym_id=payment.gym_id,
        member_id=payment.member_id,
        member_name=member.name if member else None,
        member_email=member.email if member else None,
        membership_id=payment.membership_id,
        plan_name=plan_name,
        amount=float(payment.amount),
        currency=payment.currency,
        status="paid",
        payment_method=payment.payment_method,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        payment_link_id=payment.payment_link_id,
        due_date=payment.due_date,
        paid_at=payment.paid_at,
        failure_reason=None,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


async def simulate_payment_failure(
    session: AsyncSession,
    gym_id: uuid.UUID,
    payment_id: uuid.UUID,
    failure_reason: str = "Transaction declined by issuing bank / UPI timeout",
) -> PaymentResponse:
    payment = await session.get(Payment, payment_id)
    if not payment or payment.gym_id != gym_id:
        raise ResourceNotFoundException("Payment", payment_id)

    payment.status = "failed"
    payment.failure_reason = failure_reason

    # Add reminder log
    reminder = PaymentReminder(
        gym_id=gym_id,
        member_id=payment.member_id,
        payment_id=payment.id,
        reminder_type="payment_failed",
        title="Payment Failed Alert",
        message=f"Payment of ₹{float(payment.amount):,.0f} failed. Reason: {failure_reason}",
        channel="in_app",
        status="sent",
    )
    session.add(reminder)

    await session.commit()
    await session.refresh(payment)

    # Recompute metrics to reflect at-risk status
    await compute_and_save_daily_metrics(session, gym_id=gym_id, metric_date=date.today())

    member = await session.get(Member, payment.member_id)
    return PaymentResponse(
        id=payment.id,
        gym_id=payment.gym_id,
        member_id=payment.member_id,
        member_name=member.name if member else None,
        member_email=member.email if member else None,
        membership_id=payment.membership_id,
        amount=float(payment.amount),
        currency=payment.currency,
        status="failed",
        payment_method=payment.payment_method,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        payment_link_id=payment.payment_link_id,
        due_date=payment.due_date,
        paid_at=payment.paid_at,
        failure_reason=payment.failure_reason,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


async def cancel_payment(
    session: AsyncSession, gym_id: uuid.UUID, payment_id: uuid.UUID
) -> PaymentResponse:
    payment = await session.get(Payment, payment_id)
    if not payment or payment.gym_id != gym_id:
        raise ResourceNotFoundException("Payment", payment_id)

    if payment.status == "paid":
        raise FitFlowException("BadRequest", "Cannot cancel an already completed payment", 400)

    payment.status = "cancelled"
    await session.commit()
    await session.refresh(payment)

    member = await session.get(Member, payment.member_id)
    return PaymentResponse(
        id=payment.id,
        gym_id=payment.gym_id,
        member_id=payment.member_id,
        member_name=member.name if member else None,
        amount=float(payment.amount),
        currency=payment.currency,
        status="cancelled",
        payment_method=payment.payment_method,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


async def retry_payment(
    session: AsyncSession, gym_id: uuid.UUID, payment_id: uuid.UUID
) -> PaymentResponse:
    payment = await session.get(Payment, payment_id)
    if not payment or payment.gym_id != gym_id:
        raise ResourceNotFoundException("Payment", payment_id)

    if payment.status not in ("failed", "cancelled"):
        raise FitFlowException("BadRequest", "Only failed or cancelled payments can be retried", 400)

    payment.status = "pending"
    payment.failure_reason = None
    await session.commit()
    await session.refresh(payment)

    member = await session.get(Member, payment.member_id)
    return PaymentResponse(
        id=payment.id,
        gym_id=payment.gym_id,
        member_id=payment.member_id,
        member_name=member.name if member else None,
        amount=float(payment.amount),
        currency=payment.currency,
        status="pending",
        payment_method=payment.payment_method,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


# =========================================================================
# AUTO RENEWAL / RECURRING MANDATES
# =========================================================================


async def enable_auto_renewal(
    session: AsyncSession,
    gym_id: uuid.UUID,
    member_id: uuid.UUID,
    membership_id: Optional[uuid.UUID] = None,
) -> PaymentSubscriptionResponse:
    member = await session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise ResourceNotFoundException("Member", member_id)

    if membership_id:
        mship = await session.get(Membership, membership_id)
    else:
        # Find latest membership
        m_res = await session.execute(
            select(Membership)
            .where(Membership.gym_id == gym_id, Membership.member_id == member_id)
            .order_by(desc(Membership.end_date))
        )
        mship = m_res.scalars().first()

    if not mship or mship.gym_id != gym_id:
        raise FitFlowException("BadRequest", "No active membership found for member to attach auto-renewal mandate", 400)

    plan = await session.get(MembershipPlan, mship.plan_id)
    if not plan or plan.gym_id != gym_id:
        raise ResourceNotFoundException("MembershipPlan", mship.plan_id)

    # Determine interval
    interval = "monthly"
    if plan.duration_days >= 300:
        interval = "annual"
    elif plan.duration_days >= 80:
        interval = "quarterly"

    today = date.today()
    next_billing = max(mship.end_date, today)

    # Provider mandate registration
    provider = get_payment_provider("demo")
    sub_res = await provider.create_recurring_subscription(
        amount=float(plan.price),
        currency="INR",
        member_id=member.id,
        membership_id=mship.id,
        billing_interval=interval,
        next_billing_date=next_billing,
    )

    # Upsert subscription record
    existing_sub_res = await session.execute(
        select(PaymentSubscription).where(
            PaymentSubscription.gym_id == gym_id,
            PaymentSubscription.member_id == member.id,
        )
    )
    existing_sub = existing_sub_res.scalars().first()

    if existing_sub:
        existing_sub.membership_id = mship.id
        existing_sub.provider_subscription_id = sub_res.provider_subscription_id
        existing_sub.amount = plan.price
        existing_sub.billing_interval = interval
        existing_sub.status = "active"
        existing_sub.next_billing_date = next_billing
        sub = existing_sub
    else:
        sub = PaymentSubscription(
            gym_id=gym_id,
            member_id=member.id,
            membership_id=mship.id,
            provider=provider.provider_name,
            provider_subscription_id=sub_res.provider_subscription_id,
            amount=plan.price,
            currency="INR",
            billing_interval=interval,
            status="active",
            start_date=today,
            next_billing_date=next_billing,
        )
        session.add(sub)

    # Add audit reminder log
    reminder = PaymentReminder(
        gym_id=gym_id,
        member_id=member.id,
        reminder_type="mandate_enabled",
        title="Auto-Renewal Mandate Activated",
        message=f"Recurring billing enabled for {plan.name} at ₹{float(plan.price):,.0f} ({interval}). Next charge on {next_billing}.",
        channel="in_app",
        status="sent",
    )
    session.add(reminder)

    await session.commit()
    await session.refresh(sub)

    return PaymentSubscriptionResponse(
        id=sub.id,
        gym_id=sub.gym_id,
        member_id=sub.member_id,
        member_name=member.name,
        member_email=member.email,
        membership_id=sub.membership_id,
        plan_name=plan.name,
        provider=sub.provider,
        provider_subscription_id=sub.provider_subscription_id,
        amount=float(sub.amount),
        currency=sub.currency,
        billing_interval=sub.billing_interval,
        status=sub.status,
        start_date=sub.start_date,
        next_billing_date=sub.next_billing_date,
        end_date=sub.end_date,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


async def cancel_auto_renewal(
    session: AsyncSession, gym_id: uuid.UUID, subscription_id: uuid.UUID
) -> PaymentSubscriptionResponse:
    sub = await session.get(PaymentSubscription, subscription_id)
    if not sub or sub.gym_id != gym_id:
        raise ResourceNotFoundException("PaymentSubscription", subscription_id)

    sub.status = "cancelled"
    sub.end_date = date.today()

    provider = get_payment_provider(sub.provider)
    if sub.provider_subscription_id:
        await provider.cancel_recurring_subscription(sub.provider_subscription_id)

    # Audit reminder
    reminder = PaymentReminder(
        gym_id=gym_id,
        member_id=sub.member_id,
        reminder_type="mandate_cancelled",
        title="Auto-Renewal Mandate Cancelled",
        message="Automatic renewal has been disabled. Upcoming memberships will require manual payment.",
        channel="in_app",
        status="sent",
    )
    session.add(reminder)

    await session.commit()
    await session.refresh(sub)

    member = await session.get(Member, sub.member_id)
    membership = await session.get(Membership, sub.membership_id)
    plan_name = None
    if membership:
        plan = await session.get(MembershipPlan, membership.plan_id)
        plan_name = plan.name if plan else None

    return PaymentSubscriptionResponse(
        id=sub.id,
        gym_id=sub.gym_id,
        member_id=sub.member_id,
        member_name=member.name if member else None,
        member_email=member.email if member else None,
        membership_id=sub.membership_id,
        plan_name=plan_name,
        provider=sub.provider,
        provider_subscription_id=sub.provider_subscription_id,
        amount=float(sub.amount),
        currency=sub.currency,
        billing_interval=sub.billing_interval,
        status="cancelled",
        start_date=sub.start_date,
        next_billing_date=sub.next_billing_date,
        end_date=sub.end_date,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


async def get_member_subscription(
    session: AsyncSession, gym_id: uuid.UUID, member_id: uuid.UUID
) -> Optional[PaymentSubscriptionResponse]:
    query = (
        select(PaymentSubscription, Member, MembershipPlan.name.label("plan_name"))
        .join(Member, PaymentSubscription.member_id == Member.id)
        .join(Membership, PaymentSubscription.membership_id == Membership.id)
        .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .where(
            PaymentSubscription.gym_id == gym_id,
            PaymentSubscription.member_id == member_id,
        )
        .order_by(desc(PaymentSubscription.created_at))
    )
    res = await session.execute(query)
    row = res.first()
    if not row:
        return None

    sub, mem, plan_name = row
    return PaymentSubscriptionResponse(
        id=sub.id,
        gym_id=sub.gym_id,
        member_id=sub.member_id,
        member_name=mem.name,
        member_email=mem.email,
        membership_id=sub.membership_id,
        plan_name=plan_name,
        provider=sub.provider,
        provider_subscription_id=sub.provider_subscription_id,
        amount=float(sub.amount),
        currency=sub.currency,
        billing_interval=sub.billing_interval,
        status=sub.status,
        start_date=sub.start_date,
        next_billing_date=sub.next_billing_date,
        end_date=sub.end_date,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


async def simulate_recurring_success(
    session: AsyncSession, gym_id: uuid.UUID, subscription_id: uuid.UUID
) -> PaymentSubscriptionResponse:
    sub = await session.get(PaymentSubscription, subscription_id)
    if not sub or sub.gym_id != gym_id:
        raise ResourceNotFoundException("PaymentSubscription", subscription_id)

    membership = await session.get(Membership, sub.membership_id)
    if not membership:
        raise ResourceNotFoundException("Membership", sub.membership_id)

    plan = await session.get(MembershipPlan, membership.plan_id)
    duration = plan.duration_days if plan else 30

    now = datetime.now(timezone.utc)
    today = date.today()

    # 1. Create a paid payment transaction
    payment = Payment(
        gym_id=gym_id,
        member_id=sub.member_id,
        membership_id=membership.id,
        amount=sub.amount,
        currency=sub.currency,
        status="paid",
        payment_method="upi",
        provider=sub.provider,
        provider_payment_id=f"pay_rec_{uuid.uuid4().hex[:12]}",
        paid_at=now,
        due_date=today,
    )
    session.add(payment)

    # 2. Extend membership duration
    old_end = max(membership.end_date, today)
    new_end = old_end + timedelta(days=duration)
    membership.end_date = new_end
    membership.status = "active"

    # 3. Update subscription state
    sub.status = "active"
    sub.next_billing_date = new_end

    # 4. Audit notification
    reminder = PaymentReminder(
        gym_id=gym_id,
        member_id=sub.member_id,
        payment_id=payment.id,
        reminder_type="renewal_success",
        title="Membership Auto-Renewed",
        message=f"Subscription renewed successfully for ₹{float(sub.amount):,.0f}. Coverage extended through {new_end}.",
        channel="in_app",
        status="sent",
    )
    session.add(reminder)

    await session.commit()
    await session.refresh(sub)

    # Recompute daily metrics
    await compute_and_save_daily_metrics(session, gym_id=gym_id, metric_date=today)

    member = await session.get(Member, sub.member_id)
    return PaymentSubscriptionResponse(
        id=sub.id,
        gym_id=sub.gym_id,
        member_id=sub.member_id,
        member_name=member.name if member else None,
        member_email=member.email if member else None,
        membership_id=sub.membership_id,
        plan_name=plan.name if plan else None,
        provider=sub.provider,
        provider_subscription_id=sub.provider_subscription_id,
        amount=float(sub.amount),
        currency=sub.currency,
        billing_interval=sub.billing_interval,
        status=sub.status,
        start_date=sub.start_date,
        next_billing_date=sub.next_billing_date,
        end_date=sub.end_date,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


async def simulate_recurring_failure(
    session: AsyncSession,
    gym_id: uuid.UUID,
    subscription_id: uuid.UUID,
    failure_reason: str = "Recurring mandate charge declined by bank",
) -> PaymentSubscriptionResponse:
    sub = await session.get(PaymentSubscription, subscription_id)
    if not sub or sub.gym_id != gym_id:
        raise ResourceNotFoundException("PaymentSubscription", subscription_id)

    membership = await session.get(Membership, sub.membership_id)
    plan = await session.get(MembershipPlan, membership.plan_id) if membership else None

    now = datetime.now(timezone.utc)
    today = date.today()

    # 1. Create a failed payment transaction
    payment = Payment(
        gym_id=gym_id,
        member_id=sub.member_id,
        membership_id=sub.membership_id,
        amount=sub.amount,
        currency=sub.currency,
        status="failed",
        payment_method="upi",
        provider=sub.provider,
        provider_payment_id=f"pay_rec_fail_{uuid.uuid4().hex[:12]}",
        failure_reason=failure_reason,
        paid_at=None,
        due_date=today,
    )
    session.add(payment)

    # 2. Mark subscription as past_due (DO NOT extend membership!)
    sub.status = "past_due"

    # 3. Audit reminder
    reminder = PaymentReminder(
        gym_id=gym_id,
        member_id=sub.member_id,
        payment_id=payment.id,
        reminder_type="payment_failed",
        title="Auto-Renewal Failed",
        message=f"Automatic renewal for ₹{float(sub.amount):,.0f} failed: {failure_reason}. Retry required.",
        channel="in_app",
        status="sent",
    )
    session.add(reminder)

    await session.commit()
    await session.refresh(sub)

    # Recompute metrics to reflect at-risk state
    await compute_and_save_daily_metrics(session, gym_id=gym_id, metric_date=today)

    member = await session.get(Member, sub.member_id)
    return PaymentSubscriptionResponse(
        id=sub.id,
        gym_id=sub.gym_id,
        member_id=sub.member_id,
        member_name=member.name if member else None,
        member_email=member.email if member else None,
        membership_id=sub.membership_id,
        plan_name=plan.name if plan else None,
        provider=sub.provider,
        provider_subscription_id=sub.provider_subscription_id,
        amount=float(sub.amount),
        currency=sub.currency,
        billing_interval=sub.billing_interval,
        status=sub.status,
        start_date=sub.start_date,
        next_billing_date=sub.next_billing_date,
        end_date=sub.end_date,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


async def process_due_payments(
    session: AsyncSession, gym_id: uuid.UUID
) -> DuePaymentsProcessResponse:
    """
    Idempotent batch processing of all subscriptions whose next_billing_date <= today.
    Guarantees no duplicate charges if run multiple times on the same day.
    """
    today = date.today()
    query = (
        select(PaymentSubscription, Membership, MembershipPlan, Member)
        .join(Membership, PaymentSubscription.membership_id == Membership.id)
        .join(MembershipPlan, Membership.plan_id == MembershipPlan.id)
        .join(Member, PaymentSubscription.member_id == Member.id)
        .where(
            PaymentSubscription.gym_id == gym_id,
            PaymentSubscription.status == "active",
            PaymentSubscription.next_billing_date <= today,
        )
    )
    res = await session.execute(query)
    due_items = res.all()

    processed = 0
    succeeded = 0
    failed = 0
    total_collected = 0.0
    details = []

    now = datetime.now(timezone.utc)
    for sub, mship, plan, mem in due_items:
        processed += 1

        # IDEMPOTENCY CHECK: Check if a payment for this member/membership was already created today
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        dup_check = await session.execute(
            select(Payment.id).where(
                Payment.gym_id == gym_id,
                Payment.member_id == mem.id,
                Payment.membership_id == mship.id,
                Payment.status == "paid",
                Payment.created_at >= today_start,
            )
        )
        if dup_check.scalar():
            # Already charged for today's cycle! Advance billing date if not advanced yet
            if sub.next_billing_date <= today:
                sub.next_billing_date = mship.end_date
                await session.commit()
            details.append({
                "member_name": mem.name,
                "amount": float(sub.amount),
                "status": "already_processed",
                "message": "Payment already completed for this billing window.",
            })
            continue

        # Charge via provider
        try:
            # Create payment
            payment = Payment(
                gym_id=gym_id,
                member_id=mem.id,
                membership_id=mship.id,
                amount=sub.amount,
                currency=sub.currency,
                status="paid",
                payment_method="upi",
                provider=sub.provider,
                provider_payment_id=f"pay_batch_{uuid.uuid4().hex[:12]}",
                paid_at=now,
                due_date=today,
            )
            session.add(payment)

            # Extend membership
            new_end = max(mship.end_date, today) + timedelta(days=plan.duration_days)
            mship.end_date = new_end
            mship.status = "active"

            # Advance subscription
            sub.next_billing_date = new_end
            sub.status = "active"

            # Reminder
            reminder = PaymentReminder(
                gym_id=gym_id,
                member_id=mem.id,
                payment_id=payment.id,
                reminder_type="renewal_success",
                title="Automated Billing Successful",
                message=f"Billed ₹{float(sub.amount):,.0f} for {plan.name}. Next billing {new_end}.",
                channel="in_app",
                status="sent",
            )
            session.add(reminder)

            succeeded += 1
            total_collected += float(sub.amount)
            details.append({
                "member_name": mem.name,
                "amount": float(sub.amount),
                "status": "paid",
                "next_billing_date": str(new_end),
            })
        except Exception as e:
            failed += 1
            sub.status = "past_due"
            details.append({
                "member_name": mem.name,
                "amount": float(sub.amount),
                "status": "failed",
                "error": str(e),
            })

    if processed > 0:
        await session.commit()
        await compute_and_save_daily_metrics(session, gym_id=gym_id, metric_date=today)

    return DuePaymentsProcessResponse(
        processed=processed,
        succeeded=succeeded,
        failed=failed,
        total_collected=total_collected,
        details=details,
    )


async def handle_payment_webhook(
    session: AsyncSession,
    provider_name: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    provider = get_payment_provider(provider_name)
    webhook_res = await provider.handle_webhook(payload, headers)

    # 1. Idempotency Check: Don't process duplicate webhook events
    existing = await session.execute(
        select(PaymentWebhookEvent).where(
            PaymentWebhookEvent.provider == provider_name,
            PaymentWebhookEvent.provider_event_id == webhook_res.event_id,
        )
    )
    if existing.scalar():
        return {"status": "duplicate", "event_id": webhook_res.event_id, "processed": True}

    # Record event
    event = PaymentWebhookEvent(
        provider=provider_name,
        provider_event_id=webhook_res.event_id,
        event_type=webhook_res.event_type,
        payload=payload,
        processed=True,
        processed_at=datetime.now(timezone.utc),
    )
    session.add(event)
    await session.commit()

    return {"status": "processed", "event_id": webhook_res.event_id}
