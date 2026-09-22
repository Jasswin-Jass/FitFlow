import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.member import Member
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.models.payment import Payment


async def calculate_active_members(
    session: AsyncSession, gym_id: uuid.UUID, target_date: date
) -> int:
    """
    Deterministically counts members with at least one active membership valid on target_date.
    Formula: COUNT(DISTINCT member_id) WHERE status='active' AND target_date BETWEEN start_date AND end_date
    """
    stmt = (
        select(func.count(func.distinct(Membership.member_id)))
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.start_date <= target_date,
            Membership.end_date >= target_date,
        )
    )
    result = await session.execute(stmt)
    return result.scalar() or 0


async def calculate_mrr(
    session: AsyncSession, gym_id: uuid.UUID, target_date: date
) -> float:
    """
    Deterministically calculates Monthly Recurring Revenue (MRR) for active memberships valid on target_date.
    Formula: SUM(plan.price * (30.0 / plan.duration_days)) for all active memberships valid on target_date.
    """
    stmt = (
        select(MembershipPlan.price, MembershipPlan.duration_days)
        .join(Membership, Membership.plan_id == MembershipPlan.id)
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.start_date <= target_date,
            Membership.end_date >= target_date,
        )
    )
    result = await session.execute(stmt)
    rows = result.all()
    
    total_mrr = 0.0
    for price, duration_days in rows:
        if duration_days and duration_days > 0:
            monthly_normalized = float(price) * (30.0 / float(duration_days))
            total_mrr += monthly_normalized

    return round(total_mrr, 2)


async def calculate_renewal_rate(
    session: AsyncSession, gym_id: uuid.UUID, target_date: date, window_days: int = 30
) -> Optional[float]:
    """
    Deterministically calculates the renewal rate over a rolling window (default 30 days).
    Formula: (Members who renewed / Total members whose membership ended in the window) * 100.
    
    CRITICAL RULE:
    If no memberships ended in the window (eligible population = 0), return None (JSON null).
    This distinguishes 'no renewals due' from '0.0% of members renewed'.
    """
    window_start = target_date - timedelta(days=window_days)

    # Find memberships that ended within the window
    ended_stmt = (
        select(Membership.id, Membership.member_id, Membership.end_date)
        .where(
            Membership.gym_id == gym_id,
            Membership.end_date >= window_start,
            Membership.end_date <= target_date,
        )
    )
    ended_res = await session.execute(ended_stmt)
    ended_memberships = ended_res.all()

    if not ended_memberships:
        return None

    # Get distinct members whose memberships ended in the window
    distinct_ended_members = {m.member_id for m in ended_memberships}
    if not distinct_ended_members:
        return None

    renewed_count = 0
    for m_id in distinct_ended_members:
        # Check if member has a subsequent membership that extends beyond target_date
        # or has status 'active' or started on/after window_start
        subsequent_stmt = (
            select(Membership.id)
            .where(
                Membership.gym_id == gym_id,
                Membership.member_id == m_id,
                or_(
                    Membership.status == "active",
                    Membership.end_date > target_date,
                    Membership.start_date >= window_start,
                ),
                ~Membership.id.in_([m.id for m in ended_memberships if m.member_id == m_id and m.end_date <= target_date])
            )
            .limit(1)
        )
        subsequent_res = await session.execute(subsequent_stmt)
        if subsequent_res.scalar() is not None:
            renewed_count += 1

    rate = (renewed_count / len(distinct_ended_members)) * 100.0
    return round(min(100.0, max(0.0, rate)), 2)


async def get_at_risk_members_data(
    session: AsyncSession, gym_id: uuid.UUID, target_date: date
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Deterministically identifies at-risk members:
    Rule 1: Active membership expiring within 7 days (target_date <= end_date <= target_date + 7 days)
    Rule 2: Member has a failed payment within the last 30 days without a subsequent successful payment.
    """
    seven_days_ahead = target_date + timedelta(days=7)
    thirty_days_ago = target_date - timedelta(days=30)
    thirty_days_ago_dt = datetime.combine(thirty_days_ago, datetime.min.time()).replace(tzinfo=timezone.utc)

    at_risk_dict: Dict[uuid.UUID, Dict[str, Any]] = {}

    # 1. Check expiring memberships
    expiring_stmt = (
        select(Membership, Member)
        .join(Member, Membership.member_id == Member.id)
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.end_date >= target_date,
            Membership.end_date <= seven_days_ahead,
        )
        .order_by(Membership.end_date.asc())
    )
    expiring_res = await session.execute(expiring_stmt)
    for mship, member in expiring_res.all():
        days_left = (mship.end_date - target_date).days
        reason = f"Membership expiring in {days_left} day{'s' if days_left != 1 else ''}"
        at_risk_dict[member.id] = {
            "member_id": member.id,
            "name": member.name,
            "email": member.email,
            "phone": member.phone,
            "risk_reason": reason,
            "membership_id": mship.id,
            "expiry_date": mship.end_date,
            "days_remaining": days_left,
            "failed_payment_amount": None,
        }

    # 2. Check failed payments in last 30 days
    failed_stmt = (
        select(Payment, Member)
        .join(Member, Payment.member_id == Member.id)
        .where(
            Payment.gym_id == gym_id,
            Payment.status == "failed",
            Payment.paid_at >= thirty_days_ago_dt,
        )
        .order_by(Payment.paid_at.desc())
    )
    failed_res = await session.execute(failed_stmt)
    for pmt, member in failed_res.all():
        # Check if member made a subsequent successful payment after this failed one
        subsequent_paid_stmt = (
            select(Payment.id)
            .where(
                Payment.gym_id == gym_id,
                Payment.member_id == member.id,
                Payment.status == "paid",
                Payment.paid_at > pmt.paid_at,
            )
            .limit(1)
        )
        sub_paid_res = await session.execute(subsequent_paid_stmt)
        if sub_paid_res.scalar() is None:
            # No subsequent payment! This member is at risk
            if member.id in at_risk_dict:
                at_risk_dict[member.id]["risk_reason"] += f" & Unresolved failed payment of ₹{pmt.amount:,.0f}"
                at_risk_dict[member.id]["failed_payment_amount"] = float(pmt.amount)
            else:
                at_risk_dict[member.id] = {
                    "member_id": member.id,
                    "name": member.name,
                    "email": member.email,
                    "phone": member.phone,
                    "risk_reason": f"Unresolved failed payment of ₹{pmt.amount:,.0f}",
                    "membership_id": pmt.membership_id,
                    "expiry_date": None,
                    "days_remaining": None,
                    "failed_payment_amount": float(pmt.amount),
                }

    items = list(at_risk_dict.values())
    return len(items), items
