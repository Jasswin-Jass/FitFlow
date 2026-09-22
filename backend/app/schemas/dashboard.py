import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class KpiMetric(BaseModel):
    value: Optional[float] = None
    formatted_value: str
    change_value: Optional[float] = None
    change_percentage: Optional[float] = None
    trend_direction: str = "neutral"  # "up", "down", "neutral"
    comparison_label: str = "vs previous period"


class AtRiskMemberItem(BaseModel):
    member_id: uuid.UUID
    name: str
    email: str
    phone: str
    risk_reason: str
    membership_id: Optional[uuid.UUID] = None
    expiry_date: Optional[date] = None
    days_remaining: Optional[int] = None
    failed_payment_amount: Optional[float] = None


class HistoricalMetricPoint(BaseModel):
    metric_date: date
    active_members: int
    mrr: float
    renewal_rate: Optional[float] = None
    at_risk_count: int


class PlanDistributionItem(BaseModel):
    plan_name: str
    active_count: int
    mrr_contribution: float


class DashboardSummaryResponse(BaseModel):
    gym_id: uuid.UUID
    gym_name: str
    metric_date: date
    has_data: bool
    active_members: KpiMetric
    mrr: KpiMetric
    renewal_rate: KpiMetric
    at_risk_members: KpiMetric
    at_risk_list: List[AtRiskMemberItem]
    history: List[HistoricalMetricPoint]
    plan_distribution: List[PlanDistributionItem]
