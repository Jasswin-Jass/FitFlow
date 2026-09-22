import uuid
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gym import Gym
from app.models.summary_metrics import SummaryMetric
from app.models.membership import Membership
from app.models.membership_plan import MembershipPlan
from app.analytics.metrics import (
    calculate_active_members,
    calculate_mrr,
    calculate_renewal_rate,
    get_at_risk_members_data,
)
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    KpiMetric,
    AtRiskMemberItem,
    HistoricalMetricPoint,
    PlanDistributionItem,
)
from app.core.exceptions import ResourceNotFoundException


def _format_inr(amount: float) -> str:
    """Formats an amount into Indian numbering system (e.g., ₹1.45L or ₹1,500)."""
    if amount >= 100000:
        lakhs = amount / 100000.0
        return f"₹{lakhs:.2f}L"
    return f"₹{amount:,.0f}"


async def compute_and_save_daily_metrics(
    session: AsyncSession, gym_id: uuid.UUID, metric_date: Optional[date] = None
) -> SummaryMetric:
    """
    Computes daily aggregated metrics for a gym and target date, then upserts into summary_metrics.
    """
    if metric_date is None:
        metric_date = date.today()

    active_members = await calculate_active_members(session, gym_id, metric_date)
    mrr = await calculate_mrr(session, gym_id, metric_date)
    renewal_rate = await calculate_renewal_rate(session, gym_id, metric_date)
    at_risk_count, _ = await get_at_risk_members_data(session, gym_id, metric_date)

    # Check if a summary record already exists for this gym and date
    stmt = select(SummaryMetric).where(
        SummaryMetric.gym_id == gym_id,
        SummaryMetric.metric_date == metric_date,
    )
    result = await session.execute(stmt)
    metric_record = result.scalar_one_or_none()

    if metric_record:
        metric_record.active_members = active_members
        metric_record.mrr = mrr
        metric_record.renewal_rate = renewal_rate
        metric_record.at_risk_count = at_risk_count
    else:
        metric_record = SummaryMetric(
            gym_id=gym_id,
            metric_date=metric_date,
            active_members=active_members,
            mrr=mrr,
            renewal_rate=renewal_rate,
            at_risk_count=at_risk_count,
            new_members=0,
            churned_members=0,
        )
        session.add(metric_record)

    await session.commit()
    await session.refresh(metric_record)
    return metric_record


async def get_dashboard_summary(
    session: AsyncSession, gym_id: uuid.UUID
) -> DashboardSummaryResponse:
    """
    Reads precomputed metrics from summary_metrics for the hero Business Intelligence dashboard.
    Calculates genuine comparison deltas against historical summary records.
    """
    # 1. Fetch gym
    gym = await session.get(Gym, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym", gym_id)

    today = date.today()

    # 2. Get latest summary metric
    latest_stmt = (
        select(SummaryMetric)
        .where(SummaryMetric.gym_id == gym_id)
        .order_by(SummaryMetric.metric_date.desc())
        .limit(1)
    )
    latest_res = await session.execute(latest_stmt)
    curr_metric = latest_res.scalar_one_or_none()

    # If no metrics exist, or if the latest is not for today, recompute
    if not curr_metric or curr_metric.metric_date != today:
        curr_metric = await compute_and_save_daily_metrics(session, gym_id, today)

    # 3. Fetch previous comparison metric (e.g. 7 days ago or the next most recent distinct date)
    prev_stmt = (
        select(SummaryMetric)
        .where(
            SummaryMetric.gym_id == gym_id,
            SummaryMetric.metric_date < curr_metric.metric_date,
        )
        .order_by(SummaryMetric.metric_date.desc())
        .limit(1)
    )
    prev_res = await session.execute(prev_stmt)
    prev_metric = prev_res.scalar_one_or_none()

    # 4. Calculate trend deltas
    def calculate_trend(curr_val: float, prev_val: Optional[float], is_percentage: bool = False, is_inverse: bool = False) -> KpiMetric:
        if prev_val is None:
            return KpiMetric(
                value=round(curr_val, 2),
                formatted_value=f"{curr_val:.1f}%" if is_percentage else str(int(curr_val)),
                change_value=None,
                change_percentage=None,
                trend_direction="neutral",
                comparison_label="No prior period",
            )
        
        diff = curr_val - prev_val
        pct = ((diff / prev_val) * 100.0) if prev_val > 0 else (100.0 if diff > 0 else 0.0)

        # For at-risk members, a decrease is positive ("up" indicator / green)
        if is_inverse:
            direction = "down" if diff > 0 else ("up" if diff < 0 else "neutral")
        else:
            direction = "up" if diff > 0 else ("down" if diff < 0 else "neutral")

        label = f"{'+' if diff >= 0 else ''}{pct:.1f}% vs last period" if not is_percentage else f"{'+' if diff >= 0 else ''}{diff:.1f}% pts vs last period"

        return KpiMetric(
            value=round(curr_val, 2),
            formatted_value=f"{curr_val:.1f}%" if is_percentage else str(int(curr_val)),
            change_value=round(diff, 2),
            change_percentage=round(pct, 1),
            trend_direction=direction,
            comparison_label=label,
        )

    # Active Members KPI
    active_kpi = calculate_trend(
        float(curr_metric.active_members),
        float(prev_metric.active_members) if prev_metric else None,
    )

    # MRR KPI
    mrr_val = float(curr_metric.mrr)
    prev_mrr = float(prev_metric.mrr) if prev_metric else None
    if prev_mrr is not None:
        mrr_diff = mrr_val - prev_mrr
        mrr_pct = ((mrr_diff / prev_mrr) * 100.0) if prev_mrr > 0 else (100.0 if mrr_diff > 0 else 0.0)
        mrr_dir = "up" if mrr_diff > 0 else ("down" if mrr_diff < 0 else "neutral")
        mrr_label = f"{'+' if mrr_diff >= 0 else ''}{mrr_pct:.1f}% vs last period"
    else:
        mrr_diff, mrr_pct, mrr_dir, mrr_label = None, None, "neutral", "No prior period"

    mrr_kpi = KpiMetric(
        value=round(mrr_val, 2),
        formatted_value=_format_inr(mrr_val),
        change_value=round(mrr_diff, 2) if mrr_diff is not None else None,
        change_percentage=round(mrr_pct, 1) if mrr_pct is not None else None,
        trend_direction=mrr_dir,
        comparison_label=mrr_label,
    )

    # Renewal Rate KPI
    if curr_metric.renewal_rate is None:
        renewal_kpi = KpiMetric(
            value=None,
            formatted_value="N/A",
            change_value=None,
            change_percentage=None,
            trend_direction="neutral",
            comparison_label="No renewals due in period",
        )
    else:
        renewal_kpi = calculate_trend(
            float(curr_metric.renewal_rate),
            float(prev_metric.renewal_rate) if prev_metric and prev_metric.renewal_rate is not None else None,
            is_percentage=True,
        )

    # At Risk Members KPI (inverse: decreasing is good)
    risk_diff = (curr_metric.at_risk_count - prev_metric.at_risk_count) if prev_metric else None
    risk_dir = "up" if (risk_diff or 0) < 0 else ("down" if (risk_diff or 0) > 0 else "neutral")
    risk_label = f"{'+' if (risk_diff or 0) >= 0 else ''}{risk_diff} members vs last period" if risk_diff is not None else "No prior period"

    at_risk_kpi = KpiMetric(
        value=float(curr_metric.at_risk_count),
        formatted_value=str(curr_metric.at_risk_count),
        change_value=float(risk_diff) if risk_diff is not None else None,
        change_percentage=None,
        trend_direction=risk_dir,
        comparison_label=risk_label,
    )

    # 5. Get actionable at-risk members list
    _, at_risk_raw = await get_at_risk_members_data(session, gym_id, today)
    at_risk_list = [AtRiskMemberItem(**item) for item in at_risk_raw]

    # 6. Get 30-day historical chart points
    history_stmt = (
        select(SummaryMetric)
        .where(
            SummaryMetric.gym_id == gym_id,
            SummaryMetric.metric_date >= today - timedelta(days=30),
        )
        .order_by(SummaryMetric.metric_date.asc())
    )
    history_res = await session.execute(history_stmt)
    history_rows = history_res.scalars().all()
    history = [
        HistoricalMetricPoint(
            metric_date=row.metric_date,
            active_members=row.active_members,
            mrr=float(row.mrr),
            renewal_rate=float(row.renewal_rate) if row.renewal_rate is not None else None,
            at_risk_count=row.at_risk_count,
        )
        for row in history_rows
    ]

    # 7. Plan Distribution
    plan_stmt = (
        select(
            MembershipPlan.name,
            func.count(Membership.id).label("active_count"),
            func.sum(MembershipPlan.price * (30.0 / MembershipPlan.duration_days)).label("mrr_sum"),
        )
        .join(Membership, Membership.plan_id == MembershipPlan.id)
        .where(
            Membership.gym_id == gym_id,
            Membership.status == "active",
            Membership.start_date <= today,
            Membership.end_date >= today,
        )
        .group_by(MembershipPlan.name)
    )
    plan_res = await session.execute(plan_stmt)
    plan_distribution = [
        PlanDistributionItem(
            plan_name=row.name,
            active_count=row.active_count,
            mrr_contribution=round(float(row.mrr_sum or 0), 2),
        )
        for row in plan_res.all()
    ]

    has_data = curr_metric.active_members > 0 or curr_metric.mrr > 0 or len(history) > 1

    return DashboardSummaryResponse(
        gym_id=gym.id,
        gym_name=gym.name,
        metric_date=curr_metric.metric_date,
        has_data=has_data,
        active_members=active_kpi,
        mrr=mrr_kpi,
        renewal_rate=renewal_kpi,
        at_risk_members=at_risk_kpi,
        at_risk_list=at_risk_list,
        history=history,
        plan_distribution=plan_distribution,
    )
