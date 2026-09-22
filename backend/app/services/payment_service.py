import uuid
from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.payment import Payment
from app.models.member import Member
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentListResponse
from app.core.exceptions import ResourceNotFoundException, TenantAccessDeniedException


async def list_payments(
    session: AsyncSession,
    gym_id: uuid.UUID,
    status: Optional[str] = None,
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

    if status and status in ("success", "failed", "refunded"):
        query = query.where(Payment.status == status)

    if start_date:
        start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        query = query.where(Payment.paid_at >= start_dt)

    if end_date:
        end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = query.where(Payment.paid_at <= end_dt)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await session.execute(count_query)
    total = total_res.scalar() or 0

    offset = (page - 1) * size
    query = query.order_by(desc(Payment.paid_at)).offset(offset).limit(size)
    res = await session.execute(query)
    rows = res.all()

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
            paid_at=pmt.paid_at,
            status=pmt.status,
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


async def record_payment(
    session: AsyncSession, gym_id: uuid.UUID, data: PaymentCreate
) -> PaymentResponse:
    # Verify member belongs to this gym
    member = await session.get(Member, data.member_id)
    if not member or member.gym_id != gym_id:
        raise ResourceNotFoundException("Member", data.member_id)

    # If membership_id provided, verify it belongs to this gym
    plan_name = None
    if data.membership_id:
        membership = await session.get(Membership, data.membership_id)
        if not membership or membership.gym_id != gym_id:
            raise ResourceNotFoundException("Membership", data.membership_id)
        plan = await session.get(MembershipPlan, membership.plan_id)
        plan_name = plan.name if plan else None

    payment = Payment(
        gym_id=gym_id,
        member_id=data.member_id,
        membership_id=data.membership_id,
        amount=data.amount,
        status=data.status,
        paid_at=data.paid_at or datetime.now(timezone.utc),
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
        paid_at=payment.paid_at,
        status=payment.status,
    )
