from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# 1. Overview Schema
# -------------------------------------------------------------
class KpiItem(BaseModel):
    value: Optional[float]
    formatted_value: str
    trend_percent: Optional[float] = None
    trend_direction: str = "neutral"  # up, down, neutral
    subtext: Optional[str] = None


class OverviewResponse(BaseModel):
    total_members: KpiItem
    active_members: KpiItem
    active_percent: KpiItem
    mrr: KpiItem
    renewal_rate: KpiItem
    at_risk_members: KpiItem
    has_data: bool = True


# -------------------------------------------------------------
# 2. Member Intelligence Schema
# -------------------------------------------------------------
class MemberSegmentItem(BaseModel):
    segment_name: str
    count: int
    percent: float
    description: str


class MemberIntelligenceResponse(BaseModel):
    total_members: int
    active_members: int
    inactive_members: int
    new_this_month: int
    expiring_soon_count: int
    at_risk_count: int
    avg_age: Optional[float] = None
    avg_membership_duration_days: Optional[float] = None
    avg_lifetime_value: float = 0.0
    arpu: float = 0.0
    renewal_rate: Optional[float] = None
    churn_rate: float = 0.0
    member_growth_rate_30d: float = 0.0
    segments: List[MemberSegmentItem]


# -------------------------------------------------------------
# 3. Demographics Schema
# -------------------------------------------------------------
class GenderDemographicItem(BaseModel):
    gender: str
    count: int
    percentage: float
    active_count: int
    renewal_rate: Optional[float] = None
    avg_ltv: float = 0.0


class AgeGroupItem(BaseModel):
    age_group: str  # <18, 18-24, 25-34, 35-44, 45-54, 55+
    count: int
    percentage: float
    active_count: int
    revenue_contribution: float
    renewal_rate: Optional[float] = None


class DemographicsResponse(BaseModel):
    gender_distribution: List[GenderDemographicItem]
    age_groups: List[AgeGroupItem]
    most_represented_age_group: Optional[str] = None
    fastest_growing_age_group: Optional[str] = None
    total_reported_profiles: int


# -------------------------------------------------------------
# 4. Revenue Intelligence Schema
# -------------------------------------------------------------
class PlanRevenueItem(BaseModel):
    plan_name: str
    active_count: int
    mrr_contribution: float
    percentage_of_mrr: float


class MonthlyRevenueItem(BaseModel):
    month_label: str  # e.g., "Jul 2026", "Aug 2026"
    amount: float
    transaction_count: int


class RevenueIntelligenceResponse(BaseModel):
    mrr: float
    total_revenue_all_time: float
    revenue_this_month: float
    revenue_previous_month: float
    arpu: float
    avg_transaction_value: float
    plan_breakdown: List[PlanRevenueItem]
    monthly_trend: List[MonthlyRevenueItem]
    revenue_by_gender: List[Dict[str, Any]]
    revenue_by_age_group: List[Dict[str, Any]]


# -------------------------------------------------------------
# 5. Membership Intelligence Schema
# -------------------------------------------------------------
class FunnelStage(BaseModel):
    stage: str
    count: int
    percentage_of_total: float


class MembershipIntelligenceResponse(BaseModel):
    active_count: int
    expired_count: int
    expiring_7d_count: int
    expiring_30d_count: int
    new_this_month_count: int
    renewed_this_month_count: int
    cancelled_count: int
    renewal_rate: Optional[float] = None
    churn_rate: float = 0.0
    avg_plan_duration_days: float = 0.0
    lifecycle_funnel: List[FunnelStage]


# -------------------------------------------------------------
# 6. Trainer Intelligence Schema
# -------------------------------------------------------------
class TrainerPerformanceItem(BaseModel):
    trainer_id: str
    name: str
    specialty: str
    status: str
    rating: float
    assigned_members: int
    max_capacity: int
    utilization_percent: float
    revenue_generated: float
    retention_rate: Optional[float] = None


class TrainerIntelligenceResponse(BaseModel):
    total_trainers: int
    active_trainers: int
    avg_members_per_trainer: float
    overall_utilization_percent: float
    trainers: List[TrainerPerformanceItem]
    specialization_distribution: List[Dict[str, Any]]


# -------------------------------------------------------------
# 7. Business Forecast Schema
# -------------------------------------------------------------
class ForecastMetric(BaseModel):
    metric_name: str
    current_value: float
    projected_next_month: Optional[float]
    projected_growth_percent: Optional[float]
    methodology: str
    confidence_note: str


class ForecastResponse(BaseModel):
    has_sufficient_history: bool
    status_message: str
    projection_date: date
    projected_members: ForecastMetric
    projected_mrr: ForecastMetric
    projected_renewals: ForecastMetric
    projected_churn: ForecastMetric


# -------------------------------------------------------------
# 8. Actionable Insights Schema
# -------------------------------------------------------------
class InsightItem(BaseModel):
    id: str
    type: str  # descriptive, diagnostic, forecasting, actionable
    category: str  # demographics, revenue, retention, trainers, plans
    title: str
    message: str
    metric_context: Optional[str] = None
    recommendation: Optional[str] = None
    severity: str = "info"  # info, warning, success


class InsightsResponse(BaseModel):
    insights: List[InsightItem]
    generated_at: str
