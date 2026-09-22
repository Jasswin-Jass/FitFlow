from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    OverviewResponse,
    MemberIntelligenceResponse,
    DemographicsResponse,
    RevenueIntelligenceResponse,
    MembershipIntelligenceResponse,
    TrainerIntelligenceResponse,
    ForecastResponse,
    InsightsResponse,
)
from app.analytics.analytics_service import (
    get_overview_kpis,
    get_member_intelligence,
    get_demographics,
    get_revenue_intelligence,
    get_membership_intelligence,
    get_trainer_intelligence,
    get_business_forecast,
    get_actionable_insights,
)

router = APIRouter(prefix="/analytics", tags=["Analytics & Business Intelligence"])


@router.get("/overview", response_model=OverviewResponse)
async def get_analytics_overview(
    target_date: Optional[date] = Query(None, description="Target evaluation date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns executive BI overview KPIs: Total Members, Active Members, Active %, MRR, Renewal Rate, At-Risk.
    Strictly isolated to current_user.gym_id.
    """
    return await get_overview_kpis(db, gym_id=current_user.gym_id, target_date=target_date)


@router.get("/members", response_model=MemberIntelligenceResponse)
async def get_analytics_members(
    target_date: Optional[date] = Query(None, description="Target evaluation date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns deep member intelligence: Active/Inactive counts, age stats, LTV, ARPU, churn, growth, and segmentation.
    """
    return await get_member_intelligence(db, gym_id=current_user.gym_id, target_date=target_date)


@router.get("/demographics", response_model=DemographicsResponse)
async def get_analytics_demographics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns comprehensive member demographics: Gender distribution and Age Groups (<18, 18-24, 25-34, 35-44, 45-54, 55+).
    """
    return await get_demographics(db, gym_id=current_user.gym_id)


@router.get("/revenue", response_model=RevenueIntelligenceResponse)
async def get_analytics_revenue(
    target_date: Optional[date] = Query(None, description="Target evaluation date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns revenue intelligence: MRR, total revenue, monthly comparisons, plan breakdowns, and demographic revenue.
    """
    return await get_revenue_intelligence(db, gym_id=current_user.gym_id, target_date=target_date)


@router.get("/memberships", response_model=MembershipIntelligenceResponse)
async def get_analytics_memberships(
    target_date: Optional[date] = Query(None, description="Target evaluation date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns membership lifecycle metrics: Active, Expired, Expiring cohorts, renewal/churn rates, and lifecycle funnel.
    """
    return await get_membership_intelligence(db, gym_id=current_user.gym_id, target_date=target_date)


@router.get("/trainers", response_model=TrainerIntelligenceResponse)
async def get_analytics_trainers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns trainer business metrics: Workload, capacity utilization, revenue attribution, and specialization distribution.
    """
    return await get_trainer_intelligence(db, gym_id=current_user.gym_id)


@router.get("/forecast", response_model=ForecastResponse)
async def get_analytics_forecast(
    target_date: Optional[date] = Query(None, description="Target evaluation date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns transparent trend-based statistical projections (Active members, MRR, expected renewals, expected churn).
    """
    return await get_business_forecast(db, gym_id=current_user.gym_id, target_date=target_date)


@router.get("/insights", response_model=InsightsResponse)
async def get_analytics_insights(
    target_date: Optional[date] = Query(None, description="Target evaluation date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns data-backed diagnostic, descriptive, and actionable recommendations.
    """
    return await get_actionable_insights(db, gym_id=current_user.gym_id, target_date=target_date)
