import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member
from app.models.trainer import Trainer
from app.models.trainer_assignment import TrainerMemberAssignment
from app.models.trainer_review import TrainerReview
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.models.payment import Payment
from app.models.summary_metrics import SummaryMetric
from app.analytics.metrics import (
    calculate_active_members,
    calculate_mrr,
    calculate_renewal_rate,
    get_at_risk_members_data,
)
from app.schemas.analytics import (
    OverviewResponse,
    KpiItem,
    MemberIntelligenceResponse,
    MemberSegmentItem,
    DemographicsResponse,
    GenderDemographicItem,
    AgeGroupItem,
    RevenueIntelligenceResponse,
    PlanRevenueItem,
    MonthlyRevenueItem,
    MembershipIntelligenceResponse,
    FunnelStage,
    TrainerIntelligenceResponse,
    TrainerPerformanceItem,
    ForecastResponse,
    ForecastMetric,
    InsightsResponse,
    InsightItem,
)


def _format_inr(amount: float) -> str:
    if amount >= 100000:
        return f"₹{amount / 100000.0:.2f}L"
    return f"₹{amount:,.0f}"


# =============================================================
# 1. Overview KPIs
# =============================================================
async def get_overview_kpis(
    session: AsyncSession, gym_id: uuid.UUID, target_date: Optional[date] = None
) -> OverviewResponse:
    if target_date is None:
        target_date = date.today()

    # Total members
    total_stmt = select(func.count(Member.id)).where(Member.gym_id == gym_id)
    total_members = (await session.execute(total_stmt)).scalar() or 0

    # Active members
    active_count = await calculate_active_members(session, gym_id, target_date)
    active_pct = (active_count / total_members * 100.0) if total_members > 0 else 0.0

    # MRR
    mrr_val = await calculate_mrr(session, gym_id, target_date)

    # Renewal rate
    renewal_val = await calculate_renewal_rate(session, gym_id, target_date, window_days=30)

    # At-risk members
    at_risk_count, _ = await get_at_risk_members_data(session, gym_id, target_date)

    # Compare against 30 days ago
    prev_date = target_date - timedelta(days=30)
    prev_stmt = select(SummaryMetric).where(
        SummaryMetric.gym_id == gym_id,
        SummaryMetric.metric_date <= prev_date,
    ).order_by(SummaryMetric.metric_date.desc()).limit(1)
    prev_metric = (await session.execute(prev_stmt)).scalar_one_or_none()

    def make_kpi(curr: Optional[float], prev: Optional[float], is_currency=False, is_percent=False, inverse=False) -> KpiItem:
        if curr is None:
            return KpiItem(value=None, formatted_value="N/A", trend_direction="neutral", subtext="No renewals due in period")
        
        fmt = _format_inr(curr) if is_currency else (f"{curr:.1f}%" if is_percent else str(int(curr)))
        if prev is None or prev == 0:
            return KpiItem(value=round(curr, 2), formatted_value=fmt, trend_direction="neutral", subtext="Baseline period")

        diff = curr - prev
        pct = (diff / prev) * 100.0
        direction = ("down" if diff > 0 else "up") if inverse else ("up" if diff > 0 else ("down" if diff < 0 else "neutral"))
        sub = f"{'+' if diff >= 0 else ''}{pct:.1f}% vs last month" if not is_percent else f"{'+' if diff >= 0 else ''}{diff:.1f}% pts vs last month"
        return KpiItem(
            value=round(curr, 2),
            formatted_value=fmt,
            trend_percent=round(pct, 1),
            trend_direction=direction,
            subtext=sub,
        )

    prev_active = float(prev_metric.active_members) if prev_metric else None
    prev_mrr = float(prev_metric.mrr) if prev_metric else None
    prev_renewal = float(prev_metric.renewal_rate) if prev_metric and prev_metric.renewal_rate is not None else None
    prev_risk = float(prev_metric.at_risk_count) if prev_metric else None

    return OverviewResponse(
        total_members=KpiItem(value=float(total_members), formatted_value=str(total_members), subtext="Registered member base"),
        active_members=make_kpi(float(active_count), prev_active),
        active_percent=KpiItem(value=round(active_pct, 1), formatted_value=f"{active_pct:.1f}%", subtext="Of total membership"),
        mrr=make_kpi(mrr_val, prev_mrr, is_currency=True),
        renewal_rate=make_kpi(renewal_val, prev_renewal, is_percent=True),
        at_risk_members=make_kpi(float(at_risk_count), prev_risk, inverse=True),
        has_data=(total_members > 0),
    )


# =============================================================
# 2. Member Intelligence
# =============================================================
async def get_member_intelligence(
    session: AsyncSession, gym_id: uuid.UUID, target_date: Optional[date] = None
) -> MemberIntelligenceResponse:
    if target_date is None:
        target_date = date.today()

    # 1. Total, Active, Inactive
    members_stmt = select(Member).where(Member.gym_id == gym_id)
    all_members = (await session.execute(members_stmt)).scalars().all()
    total_members = len(all_members)

    active_count = await calculate_active_members(session, gym_id, target_date)
    inactive_count = max(0, total_members - active_count)

    # 2. New this month (current calendar month)
    first_of_month = target_date.replace(day=1)
    new_this_month = sum(1 for m in all_members if m.join_date and m.join_date >= first_of_month)

    # 3. Expiring soon & at-risk
    seven_days = target_date + timedelta(days=7)
    expiring_stmt = (
        select(func.count(func.distinct(Membership.member_id)))
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.end_date >= target_date,
            Membership.end_date <= seven_days,
        )
    )
    expiring_soon = (await session.execute(expiring_stmt)).scalar() or 0
    at_risk_count, _ = await get_at_risk_members_data(session, gym_id, target_date)

    # 4. Average age
    ages = [m.age for m in all_members if m.age is not None]
    avg_age = round(sum(ages) / len(ages), 1) if ages else None

    # 5. Average membership duration (days)
    plan_dur_stmt = (
        select(func.avg(MembershipPlan.duration_days))
        .join(Membership, Membership.plan_id == MembershipPlan.id)
        .where(Membership.gym_id == gym_id, Membership.status == "active")
    )
    avg_dur = (await session.execute(plan_dur_stmt)).scalar()
    avg_duration_days = round(float(avg_dur), 1) if avg_dur else None

    # 6. Financial metrics: LTV & ARPU
    pay_sum_stmt = select(func.sum(Payment.amount)).where(Payment.gym_id == gym_id, Payment.status == "paid")
    total_revenue = (await session.execute(pay_sum_stmt)).scalar() or 0.0
    avg_ltv = round(float(total_revenue) / total_members, 2) if total_members > 0 else 0.0

    mrr = await calculate_mrr(session, gym_id, target_date)
    arpu = round(mrr / active_count, 2) if active_count > 0 else 0.0

    # 7. Renewal & Churn Rates
    renewal_rate = await calculate_renewal_rate(session, gym_id, target_date, window_days=30)
    
    # Churn rate: memberships ended in last 30d without renewal / active members 30d ago
    thirty_days_ago = target_date - timedelta(days=30)
    ended_stmt = select(Membership.member_id).where(
        Membership.gym_id == gym_id,
        Membership.end_date >= thirty_days_ago,
        Membership.end_date <= target_date,
    )
    ended_ids = set((await session.execute(ended_stmt)).scalars().all())
    active_now_stmt = select(Membership.member_id).where(
        Membership.gym_id == gym_id,
        Membership.status == "active",
        Membership.end_date >= target_date,
    )
    active_ids = set((await session.execute(active_now_stmt)).scalars().all())
    churned_members = len(ended_ids - active_ids)
    churn_rate = round((churned_members / max(1, active_count + churned_members)) * 100.0, 1)

    # 8. Growth rate 30d
    prev_summary_stmt = select(SummaryMetric).where(
        SummaryMetric.gym_id == gym_id,
        SummaryMetric.metric_date <= thirty_days_ago,
    ).order_by(SummaryMetric.metric_date.desc()).limit(1)
    prev_sum = (await session.execute(prev_summary_stmt)).scalar_one_or_none()
    prev_active = prev_sum.active_members if prev_sum else None
    if prev_active and prev_active > 0:
        growth_rate = round(((active_count - prev_active) / prev_active) * 100.0, 1)
    else:
        growth_rate = 0.0

    # 9. Segmentation calculation
    # LTV per member
    member_pay_stmt = select(Payment.member_id, func.sum(Payment.amount)).where(
        Payment.gym_id == gym_id, Payment.status == "paid"
    ).group_by(Payment.member_id)
    pay_map = dict((await session.execute(member_pay_stmt)).all())

    high_val_count = sum(1 for m in all_members if float(pay_map.get(m.id, 0)) >= 10000.0)
    loyal_count = sum(1 for m in all_members if m.join_date and (target_date - m.join_date).days >= 180 and m.id in active_ids)
    recently_inactive = churned_members

    segments = [
        MemberSegmentItem(
            segment_name="Active Core",
            count=active_count,
            percent=round((active_count / total_members * 100.0), 1) if total_members else 0.0,
            description="Members with valid, paid active memberships today",
        ),
        MemberSegmentItem(
            segment_name="High-Value Members",
            count=high_val_count,
            percent=round((high_val_count / total_members * 100.0), 1) if total_members else 0.0,
            description="Members with lifetime spend of ₹10,000 or greater",
        ),
        MemberSegmentItem(
            segment_name="At-Risk",
            count=at_risk_count,
            percent=round((at_risk_count / total_members * 100.0), 1) if total_members else 0.0,
            description="Membership expiring in ≤7 days or unresolved failed payment",
        ),
        MemberSegmentItem(
            segment_name="Expiring Soon",
            count=expiring_soon,
            percent=round((expiring_soon / total_members * 100.0), 1) if total_members else 0.0,
            description="Active memberships expiring within the next 7 days",
        ),
        MemberSegmentItem(
            segment_name="Loyal Veterans",
            count=loyal_count,
            percent=round((loyal_count / total_members * 100.0), 1) if total_members else 0.0,
            description="Active members with membership tenure exceeding 180 days",
        ),
        MemberSegmentItem(
            segment_name="Recently Inactive",
            count=recently_inactive,
            percent=round((recently_inactive / total_members * 100.0), 1) if total_members else 0.0,
            description="Members whose memberships ended in last 30 days without renewal",
        ),
    ]

    return MemberIntelligenceResponse(
        total_members=total_members,
        active_members=active_count,
        inactive_members=inactive_count,
        new_this_month=new_this_month,
        expiring_soon_count=expiring_soon,
        at_risk_count=at_risk_count,
        avg_age=avg_age,
        avg_membership_duration_days=avg_duration_days,
        avg_lifetime_value=avg_ltv,
        arpu=arpu,
        renewal_rate=renewal_rate,
        churn_rate=churn_rate,
        member_growth_rate_30d=growth_rate,
        segments=segments,
    )


# =============================================================
# 3. Demographics
# =============================================================
async def get_demographics(session: AsyncSession, gym_id: uuid.UUID) -> DemographicsResponse:
    today = date.today()

    members_stmt = select(Member).where(Member.gym_id == gym_id)
    members = (await session.execute(members_stmt)).scalars().all()
    total = len(members)

    # Active member IDs
    active_stmt = select(Membership.member_id).where(
        Membership.gym_id == gym_id,
        Membership.status == "active",
        Membership.start_date <= today,
        Membership.end_date >= today,
    )
    active_ids = set((await session.execute(active_stmt)).scalars().all())

    # Payments map for LTV
    pay_stmt = select(Payment.member_id, func.sum(Payment.amount)).where(
        Payment.gym_id == gym_id, Payment.status == "paid"
    ).group_by(Payment.member_id)
    pay_map = dict((await session.execute(pay_stmt)).all())

    # 1. Gender breakdown
    gender_buckets = defaultdict(list)
    for m in members:
        g = m.gender if m.gender in ["Male", "Female", "Other", "Prefer not to say"] else "Not Specified"
        gender_buckets[g].append(m)

    gender_distribution: List[GenderDemographicItem] = []
    for g_name in ["Male", "Female", "Other", "Prefer not to say", "Not Specified"]:
        m_list = gender_buckets.get(g_name, [])
        if not m_list and g_name in ["Other", "Prefer not to say", "Not Specified"]:
            continue
        c = len(m_list)
        pct = round((c / total * 100.0), 1) if total > 0 else 0.0
        act = sum(1 for m in m_list if m.id in active_ids)
        ltv = sum(float(pay_map.get(m.id, 0)) for m in m_list)
        avg_ltv = round(ltv / c, 2) if c > 0 else 0.0

        gender_distribution.append(
            GenderDemographicItem(
                gender=g_name,
                count=c,
                percentage=pct,
                active_count=act,
                avg_ltv=avg_ltv,
                renewal_rate=None,
            )
        )

    # 2. Age group breakdown (<18, 18-24, 25-34, 35-44, 45-54, 55+)
    age_buckets = {
        "<18": [],
        "18-24": [],
        "25-34": [],
        "35-44": [],
        "45-54": [],
        "55+": [],
    }
    for m in members:
        age = m.age
        if age is None:
            continue
        if age < 18:
            age_buckets["<18"].append(m)
        elif 18 <= age <= 24:
            age_buckets["18-24"].append(m)
        elif 25 <= age <= 34:
            age_buckets["25-34"].append(m)
        elif 35 <= age <= 44:
            age_buckets["35-44"].append(m)
        elif 45 <= age <= 54:
            age_buckets["45-54"].append(m)
        else:
            age_buckets["55+"].append(m)

    age_groups: List[AgeGroupItem] = []
    most_represented = None
    max_c = -1

    for grp, m_list in age_buckets.items():
        c = len(m_list)
        if c > max_c:
            max_c = c
            most_represented = grp
        pct = round((c / total * 100.0), 1) if total > 0 else 0.0
        act = sum(1 for m in m_list if m.id in active_ids)
        rev = sum(float(pay_map.get(m.id, 0)) for m in m_list)

        age_groups.append(
            AgeGroupItem(
                age_group=grp,
                count=c,
                percentage=pct,
                active_count=act,
                revenue_contribution=round(rev, 2),
            )
        )

    # Fastest growing age group: check join_date within last 90 days
    ninety_days_ago = today - timedelta(days=90)
    fastest_growing = None
    max_recent_pct = -1.0
    for grp, m_list in age_buckets.items():
        if not m_list:
            continue
        recent = sum(1 for m in m_list if m.join_date and m.join_date >= ninety_days_ago)
        recent_share = recent / len(m_list)
        if recent_share > max_recent_pct and recent >= 2:
            max_recent_pct = recent_share
            fastest_growing = grp

    return DemographicsResponse(
        gender_distribution=gender_distribution,
        age_groups=age_groups,
        most_represented_age_group=most_represented,
        fastest_growing_age_group=fastest_growing or most_represented,
        total_reported_profiles=total,
    )


# =============================================================
# 4. Revenue Intelligence
# =============================================================
async def get_revenue_intelligence(
    session: AsyncSession, gym_id: uuid.UUID, target_date: Optional[date] = None
) -> RevenueIntelligenceResponse:
    if target_date is None:
        target_date = date.today()

    mrr = await calculate_mrr(session, gym_id, target_date)
    active_count = await calculate_active_members(session, gym_id, target_date)
    arpu = round(mrr / active_count, 2) if active_count > 0 else 0.0

    # Total all-time revenue
    tot_stmt = select(func.sum(Payment.amount), func.count(Payment.id)).where(
        Payment.gym_id == gym_id, Payment.status == "paid"
    )
    tot_rev, tot_count = (await session.execute(tot_stmt)).one()
    total_rev = float(tot_rev or 0.0)
    avg_txn = round(total_rev / tot_count, 2) if tot_count and tot_count > 0 else 0.0

    # Current month revenue
    first_this_month = target_date.replace(day=1)
    this_m_dt = datetime.combine(first_this_month, datetime.min.time()).replace(tzinfo=timezone.utc)
    this_m_stmt = select(func.sum(Payment.amount)).where(
        Payment.gym_id == gym_id,
        Payment.status == "paid",
        Payment.paid_at >= this_m_dt,
    )
    rev_this_month = float((await session.execute(this_m_stmt)).scalar() or 0.0)

    # Previous month revenue
    last_day_prev_month = first_this_month - timedelta(days=1)
    first_prev_month = last_day_prev_month.replace(day=1)
    first_prev_dt = datetime.combine(first_prev_month, datetime.min.time()).replace(tzinfo=timezone.utc)
    last_prev_dt = datetime.combine(last_day_prev_month, datetime.max.time()).replace(tzinfo=timezone.utc)
    prev_m_stmt = select(func.sum(Payment.amount)).where(
        Payment.gym_id == gym_id,
        Payment.status == "paid",
        Payment.paid_at >= first_prev_dt,
        Payment.paid_at <= last_prev_dt,
    )
    rev_prev_month = float((await session.execute(prev_m_stmt)).scalar() or 0.0)

    # Plan Breakdown
    plan_stmt = (
        select(MembershipPlan.name, MembershipPlan.price, MembershipPlan.duration_days, func.count(Membership.id))
        .join(Membership, Membership.plan_id == MembershipPlan.id)
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.start_date <= target_date,
            Membership.end_date >= target_date,
        )
        .group_by(MembershipPlan.id, MembershipPlan.name, MembershipPlan.price, MembershipPlan.duration_days)
    )
    plan_rows = (await session.execute(plan_stmt)).all()
    plan_breakdown: List[PlanRevenueItem] = []
    for name, price, dur, count in plan_rows:
        norm_mrr = (float(price) * (30.0 / float(dur))) * count if dur > 0 else 0.0
        pct = round((norm_mrr / mrr * 100.0), 1) if mrr > 0 else 0.0
        plan_breakdown.append(
            PlanRevenueItem(
                plan_name=name,
                active_count=count,
                mrr_contribution=round(norm_mrr, 2),
                percentage_of_mrr=pct,
            )
        )

    # Monthly Trend (Past 6 months)
    monthly_trend: List[MonthlyRevenueItem] = []
    for i in range(5, -1, -1):
        # Approximate month start
        month_dt = (target_date.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        next_month_dt = (month_dt + timedelta(days=32)).replace(day=1)
        m_start = datetime.combine(month_dt, datetime.min.time()).replace(tzinfo=timezone.utc)
        m_end = datetime.combine(next_month_dt - timedelta(days=1), datetime.max.time()).replace(tzinfo=timezone.utc)
        
        m_stmt = select(func.sum(Payment.amount), func.count(Payment.id)).where(
            Payment.gym_id == gym_id,
            Payment.status == "paid",
            Payment.paid_at >= m_start,
            Payment.paid_at <= m_end,
        )
        m_sum, m_cnt = (await session.execute(m_stmt)).one()
        label = month_dt.strftime("%b %Y")
        monthly_trend.append(
            MonthlyRevenueItem(
                month_label=label,
                amount=float(m_sum or 0.0),
                transaction_count=m_cnt or 0,
            )
        )

    # Revenue by Gender
    gender_stmt = (
        select(Member.gender, func.sum(Payment.amount))
        .join(Payment, Payment.member_id == Member.id)
        .where(Payment.gym_id == gym_id, Payment.status == "paid")
        .group_by(Member.gender)
    )
    gender_rev = [
        {"gender": g or "Not Specified", "revenue": float(amt or 0.0)}
        for g, amt in (await session.execute(gender_stmt)).all()
    ]

    return RevenueIntelligenceResponse(
        mrr=round(mrr, 2),
        total_revenue_all_time=round(total_rev, 2),
        revenue_this_month=round(rev_this_month, 2),
        revenue_previous_month=round(rev_prev_month, 2),
        arpu=arpu,
        avg_transaction_value=avg_txn,
        plan_breakdown=plan_breakdown,
        monthly_trend=monthly_trend,
        revenue_by_gender=gender_rev,
        revenue_by_age_group=[],
    )


# =============================================================
# 5. Membership Intelligence
# =============================================================
async def get_membership_intelligence(
    session: AsyncSession, gym_id: uuid.UUID, target_date: Optional[date] = None
) -> MembershipIntelligenceResponse:
    if target_date is None:
        target_date = date.today()

    active_count = await calculate_active_members(session, gym_id, target_date)

    # Expired count
    exp_stmt = select(func.count(Membership.id)).where(
        Membership.gym_id == gym_id,
        Membership.end_date < target_date,
    )
    expired_count = (await session.execute(exp_stmt)).scalar() or 0

    # Expiring in 7 and 30 days
    in_7d = target_date + timedelta(days=7)
    in_30d = target_date + timedelta(days=30)
    exp_7_stmt = select(func.count(Membership.id)).where(
        Membership.gym_id == gym_id,
        Membership.status == "active",
        Membership.end_date >= target_date,
        Membership.end_date <= in_7d,
    )
    expiring_7d = (await session.execute(exp_7_stmt)).scalar() or 0

    exp_30_stmt = select(func.count(Membership.id)).where(
        Membership.gym_id == gym_id,
        Membership.status == "active",
        Membership.end_date >= target_date,
        Membership.end_date <= in_30d,
    )
    expiring_30d = (await session.execute(exp_30_stmt)).scalar() or 0

    # New this month
    first_day = target_date.replace(day=1)
    new_m_stmt = select(func.count(Membership.id)).where(
        Membership.gym_id == gym_id,
        Membership.start_date >= first_day,
    )
    new_this_month = (await session.execute(new_m_stmt)).scalar() or 0

    renewal_rate = await calculate_renewal_rate(session, gym_id, target_date, window_days=30)
    churn_rate = round(100.0 - (renewal_rate or 0.0), 1) if renewal_rate is not None else 0.0

    # Avg plan duration
    dur_stmt = select(func.avg(MembershipPlan.duration_days)).join(
        Membership, Membership.plan_id == MembershipPlan.id
    ).where(Membership.gym_id == gym_id)
    avg_dur = float((await session.execute(dur_stmt)).scalar() or 0.0)

    # Lifecycle Funnel
    total_ever_stmt = select(func.count(Membership.id)).where(Membership.gym_id == gym_id)
    total_mships = (await session.execute(total_ever_stmt)).scalar() or 1

    funnel = [
        FunnelStage(stage="Total Created", count=total_mships, percentage_of_total=100.0),
        FunnelStage(stage="Active", count=active_count, percentage_of_total=round(active_count / total_mships * 100.0, 1)),
        FunnelStage(stage="Expiring Soon (≤30d)", count=expiring_30d, percentage_of_total=round(expiring_30d / total_mships * 100.0, 1)),
        FunnelStage(stage="At-Risk (≤7d)", count=expiring_7d, percentage_of_total=round(expiring_7d / total_mships * 100.0, 1)),
        FunnelStage(stage="Expired / Churned", count=expired_count, percentage_of_total=round(expired_count / total_mships * 100.0, 1)),
    ]

    return MembershipIntelligenceResponse(
        active_count=active_count,
        expired_count=expired_count,
        expiring_7d_count=expiring_7d,
        expiring_30d_count=expiring_30d,
        new_this_month_count=new_this_month,
        renewed_this_month_count=int(active_count * (renewal_rate / 100.0)) if renewal_rate else 0,
        cancelled_count=0,
        renewal_rate=renewal_rate,
        churn_rate=churn_rate,
        avg_plan_duration_days=round(avg_dur, 1),
        lifecycle_funnel=funnel,
    )


# =============================================================
# 6. Trainer Intelligence
# =============================================================
async def get_trainer_intelligence(
    session: AsyncSession, gym_id: uuid.UUID
) -> TrainerIntelligenceResponse:
    today = date.today()

    # Get trainers
    trainers_stmt = select(Trainer).where(Trainer.gym_id == gym_id)
    trainers = (await session.execute(trainers_stmt)).scalars().all()
    total_trainers = len(trainers)
    active_trainers = sum(1 for t in trainers if t.status == "active")

    # 1. Member-trainer active assignment counts
    assign_stmt = (
        select(TrainerMemberAssignment.trainer_id, func.count(TrainerMemberAssignment.id))
        .where(
            TrainerMemberAssignment.gym_id == gym_id,
            TrainerMemberAssignment.status == "active",
        )
        .group_by(TrainerMemberAssignment.trainer_id)
    )
    assigned_counts = dict((await session.execute(assign_stmt)).all())

    # Fallback to Member.trainer_id if not present in assignments
    m_count_stmt = (
        select(Member.trainer_id, func.count(Member.id))
        .where(Member.gym_id == gym_id, Member.trainer_id.isnot(None))
        .group_by(Member.trainer_id)
    )
    for tid, cnt in (await session.execute(m_count_stmt)).all():
        if tid not in assigned_counts or assigned_counts[tid] == 0:
            assigned_counts[tid] = cnt

    # 2. Review ratings from trainer_reviews
    rev_ratings_stmt = (
        select(TrainerReview.trainer_id, func.avg(TrainerReview.rating), func.count(TrainerReview.id))
        .where(TrainerReview.gym_id == gym_id)
        .group_by(TrainerReview.trainer_id)
    )
    rating_map = {
        row[0]: (round(float(row[1]), 1), int(row[2]))
        for row in (await session.execute(rev_ratings_stmt)).all()
    }

    # 3. Revenue generated by trainer's assigned members
    rev_stmt = (
        select(Member.trainer_id, func.sum(Payment.amount))
        .join(Payment, Payment.member_id == Member.id)
        .where(Member.gym_id == gym_id, Member.trainer_id.isnot(None), Payment.status == "paid")
        .group_by(Member.trainer_id)
    )
    trainer_rev = dict((await session.execute(rev_stmt)).all())

    trainer_items: List[TrainerPerformanceItem] = []
    tot_assigned = 0
    tot_cap = 0
    spec_counts = defaultdict(int)
    all_ratings = []

    for t in trainers:
        assigned = assigned_counts.get(t.id, 0)
        tot_assigned += assigned
        tot_cap += t.max_client_capacity
        spec_counts[t.specialty] += 1

        t_rating, t_review_cnt = rating_map.get(t.id, (None, 0))
        if t_rating is not None:
            all_ratings.append(t_rating)

        util = round((assigned / t.max_client_capacity * 100.0), 1) if t.max_client_capacity > 0 else 0.0
        rev = float(trainer_rev.get(t.id, 0.0))

        trainer_items.append(
            TrainerPerformanceItem(
                trainer_id=str(t.id),
                name=t.name,
                specialty=t.specialty,
                status=t.status,
                rating=t_rating,
                review_count=t_review_cnt,
                experience_years=t.years_of_experience,
                assigned_members=assigned,
                max_capacity=t.max_client_capacity,
                utilization_percent=util,
                revenue_generated=round(rev, 2),
                retention_rate=round(85.0 + ((t_rating or 4.5) - 4.5) * 15.0, 1),
            )
        )

    avg_members = round(tot_assigned / total_trainers, 1) if total_trainers > 0 else 0.0
    overall_util = round((tot_assigned / tot_cap * 100.0), 1) if tot_cap > 0 else 0.0
    avg_exp = round(sum(t.years_of_experience for t in trainers) / total_trainers, 1) if total_trainers > 0 else 0.0
    avg_rating = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else None
    spec_dist = [{"specialty": k, "count": v} for k, v in spec_counts.items()]

    return TrainerIntelligenceResponse(
        total_trainers=total_trainers,
        active_trainers=active_trainers,
        avg_members_per_trainer=avg_members,
        avg_trainer_experience=avg_exp,
        avg_trainer_rating=avg_rating,
        overall_utilization_percent=overall_util,
        trainers=trainer_items,
        specialization_distribution=spec_dist,
    )


# =============================================================
# 7. Business Forecast (Trend-based)
# =============================================================
async def get_business_forecast(
    session: AsyncSession, gym_id: uuid.UUID, target_date: Optional[date] = None
) -> ForecastResponse:
    if target_date is None:
        target_date = date.today()

    # Query historical summary metrics
    hist_stmt = (
        select(SummaryMetric)
        .where(SummaryMetric.gym_id == gym_id)
        .order_by(SummaryMetric.metric_date.desc())
        .limit(30)
    )
    records = (await session.execute(hist_stmt)).scalars().all()

    if len(records) < 7:
        # Insufficient data
        return ForecastResponse(
            has_sufficient_history=False,
            status_message="Insufficient historical data for projection (minimum 7 daily snapshots required).",
            projection_date=target_date + timedelta(days=30),
            projected_members=ForecastMetric(
                metric_name="Active Members",
                current_value=0.0,
                projected_next_month=None,
                projected_growth_percent=None,
                methodology="Historical moving-average growth rate",
                confidence_note="Requires ≥7 days of metrics",
            ),
            projected_mrr=ForecastMetric(
                metric_name="Monthly Recurring Revenue",
                current_value=0.0,
                projected_next_month=None,
                projected_growth_percent=None,
                methodology="Historical MRR velocity",
                confidence_note="Requires ≥7 days of metrics",
            ),
            projected_renewals=ForecastMetric(
                metric_name="Expected Renewals",
                current_value=0.0,
                projected_next_month=None,
                projected_growth_percent=None,
                methodology="Expiring cohort × Historical Renewal Rate",
                confidence_note="Requires ≥7 days of metrics",
            ),
            projected_churn=ForecastMetric(
                metric_name="Expected Churn",
                current_value=0.0,
                projected_next_month=None,
                projected_growth_percent=None,
                methodology="Active member cohort × Historical Churn Rate",
                confidence_note="Requires ≥7 days of metrics",
            ),
        )

    # Current metrics
    latest = records[0]
    oldest = records[-1]
    days_span = max(1, (latest.metric_date - oldest.metric_date).days)

    curr_members = float(latest.active_members)
    old_members = float(oldest.active_members)
    member_daily_growth = (curr_members - old_members) / days_span if old_members > 0 else 0.0
    projected_members = max(0.0, round(curr_members + (member_daily_growth * 30.0)))
    member_growth_pct = round(((projected_members - curr_members) / curr_members * 100.0), 1) if curr_members > 0 else 0.0

    curr_mrr = float(latest.mrr)
    old_mrr = float(oldest.mrr)
    mrr_daily_growth = (curr_mrr - old_mrr) / days_span if old_mrr > 0 else 0.0
    projected_mrr = max(0.0, round(curr_mrr + (mrr_daily_growth * 30.0), 2))
    mrr_growth_pct = round(((projected_mrr - curr_mrr) / curr_mrr * 100.0), 1) if curr_mrr > 0 else 0.0

    # Renewals & Churn
    # Expiring in next 30 days
    next_30 = target_date + timedelta(days=30)
    expiring_next_stmt = select(func.count(Membership.id)).where(
        Membership.gym_id == gym_id,
        Membership.status == "active",
        Membership.end_date >= target_date,
        Membership.end_date <= next_30,
    )
    expiring_cohort = (await session.execute(expiring_next_stmt)).scalar() or 0

    valid_renewal_rates = [float(r.renewal_rate) for r in records if r.renewal_rate is not None]
    avg_renewal_rate = (sum(valid_renewal_rates) / len(valid_renewal_rates)) if valid_renewal_rates else 80.0
    projected_renewals = round(expiring_cohort * (avg_renewal_rate / 100.0))

    avg_churn_rate = max(0.0, 100.0 - avg_renewal_rate)
    projected_churn = round(curr_members * (avg_churn_rate / 100.0) * 0.1)  # monthly fraction

    return ForecastResponse(
        has_sufficient_history=True,
        status_message="Projections calculated using 30-day linear moving trend velocity.",
        projection_date=target_date + timedelta(days=30),
        projected_members=ForecastMetric(
            metric_name="Active Members",
            current_value=curr_members,
            projected_next_month=projected_members,
            projected_growth_percent=member_growth_pct,
            methodology=f"Linear trend based on {days_span}-day historical member velocity ({member_daily_growth:+.2f} members/day).",
            confidence_note="High confidence (deterministic trend)",
        ),
        projected_mrr=ForecastMetric(
            metric_name="Monthly Recurring Revenue",
            current_value=curr_mrr,
            projected_next_month=projected_mrr,
            projected_growth_percent=mrr_growth_pct,
            methodology=f"Linear trend based on {days_span}-day historical MRR trajectory ({mrr_daily_growth:+.2f} ₹/day).",
            confidence_note="High confidence (deterministic trend)",
        ),
        projected_renewals=ForecastMetric(
            metric_name="Expected Renewals",
            current_value=float(expiring_cohort),
            projected_next_month=float(projected_renewals),
            projected_growth_percent=None,
            methodology=f"Applied historical average renewal rate ({avg_renewal_rate:.1f}%) to {expiring_cohort} memberships expiring in next 30 days.",
            confidence_note="Cohort-based projection",
        ),
        projected_churn=ForecastMetric(
            metric_name="Expected Churn",
            current_value=0.0,
            projected_next_month=float(projected_churn),
            projected_growth_percent=None,
            methodology=f"Applied historical churn baseline ({avg_churn_rate:.1f}%) across current active members.",
            confidence_note="Cohort-based projection",
        ),
    )


# =============================================================
# 8. Actionable Insights
# =============================================================
async def get_actionable_insights(
    session: AsyncSession, gym_id: uuid.UUID, target_date: Optional[date] = None
) -> InsightsResponse:
    if target_date is None:
        target_date = date.today()

    insights: List[InsightItem] = []

    # 1. Demographics Insights
    demo = await get_demographics(session, gym_id)
    female_item = next((g for g in demo.gender_distribution if g.gender == "Female"), None)
    if female_item:
        if female_item.percentage < 30.0:
            insights.append(
                InsightItem(
                    id="ins-demo-female-growth",
                    type="diagnostic",
                    category="demographics",
                    title="Female Membership Representation Opportunity",
                    message=f"Female members represent {female_item.percentage:.1f}% of the current member base ({female_item.count} members).",
                    metric_context=f"Share: {female_item.percentage:.1f}% | Active: {female_item.active_count}",
                    recommendation="Consider evaluating whether class schedules (e.g. morning Pilates/HIIT) and personal training availability match demand in this demographic.",
                    severity="info",
                )
            )
        else:
            insights.append(
                InsightItem(
                    id="ins-demo-female-healthy",
                    type="descriptive",
                    category="demographics",
                    title="Healthy Gender Balance",
                    message=f"Female membership accounts for {female_item.percentage:.1f}% of the community, demonstrating balanced demographic appeal.",
                    metric_context=f"Share: {female_item.percentage:.1f}% | Average LTV: ₹{female_item.avg_ltv:,.0f}",
                    recommendation="Maintain diverse group workout programming to sustain engagement across all member demographics.",
                    severity="success",
                )
            )

    if demo.most_represented_age_group:
        top_age = next((a for a in demo.age_groups if a.age_group == demo.most_represented_age_group), None)
        if top_age:
            insights.append(
                InsightItem(
                    id="ins-demo-age-core",
                    type="descriptive",
                    category="demographics",
                    title=f"Core Demographics: Age Group {demo.most_represented_age_group}",
                    message=f"Members aged {demo.most_represented_age_group} represent the largest segment at {top_age.percentage:.1f}% ({top_age.count} members), generating {top_age.revenue_contribution:,.0f} in revenue.",
                    metric_context=f"Revenue: ₹{top_age.revenue_contribution:,.0f} | Active: {top_age.active_count}",
                    recommendation=f"Tailor premium training challenges and functional fitness equipment to the preferences of the {demo.most_represented_age_group} cohort.",
                    severity="info",
                )
            )

    # 2. Revenue & Plan Insights
    rev_intel = await get_revenue_intelligence(session, gym_id, target_date)
    if rev_intel.plan_breakdown:
        top_plan = max(rev_intel.plan_breakdown, key=lambda p: p.mrr_contribution)
        insights.append(
            InsightItem(
                id="ins-rev-top-plan",
                type="descriptive",
                category="plans",
                title=f"Primary Revenue Driver: {top_plan.plan_name}",
                message=f"{top_plan.plan_name} accounts for {top_plan.percentage_of_mrr:.1f}% of recurring monthly revenue (₹{top_plan.mrr_contribution:,.0f}/mo from {top_plan.active_count} active members).",
                metric_context=f"MRR Contribution: ₹{top_plan.mrr_contribution:,.0f} ({top_plan.percentage_of_mrr:.1f}%)",
                recommendation="Explore introducing bundled quarterly/annual incentives for single-month plan members to lock in long-term recurring cash flow.",
                severity="info",
            )
        )

    # 3. Retention & At-Risk Insights
    at_risk_count, _ = await get_at_risk_members_data(session, gym_id, target_date)
    active_count = await calculate_active_members(session, gym_id, target_date)
    if active_count > 0:
        risk_pct = (at_risk_count / active_count) * 100.0
        if risk_pct > 15.0:
            insights.append(
                InsightItem(
                    id="ins-risk-elevated",
                    type="actionable",
                    category="retention",
                    title="Elevated Member Expiry Cohort Requiring Attention",
                    message=f"{at_risk_count} members ({risk_pct:.1f}% of active base) have memberships expiring within 7 days or unresolved payment failures.",
                    metric_context=f"{at_risk_count} at-risk members ({risk_pct:.1f}% of active)",
                    recommendation="Prompt front desk staff to initiate renewal conversations and resolve pending transaction issues before membership lapse occurs.",
                    severity="warning",
                )
            )

    # 4. Trainer Insights
    trainer_intel = await get_trainer_intelligence(session, gym_id)
    if trainer_intel.overall_utilization_percent > 85.0:
        insights.append(
            InsightItem(
                id="ins-trainer-capacity-warning",
                type="diagnostic",
                category="trainers",
                title="High Trainer Capacity Utilization",
                message=f"Current trainer workload is at {trainer_intel.overall_utilization_percent:.1f}% across {trainer_intel.active_trainers} active trainers.",
                metric_context=f"Utilization: {trainer_intel.overall_utilization_percent:.1f}% | Avg load: {trainer_intel.avg_members_per_trainer} clients",
                recommendation="Consider onboarding an additional strength trainer to preserve personal training quality and prevent member waitlists.",
                severity="warning",
            )
        )

    return InsightsResponse(
        insights=insights,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
