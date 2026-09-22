export interface User {
  id: string;
  gym_id: string;
  gym_name?: string;
  email: string;
  role: "owner" | "trainer" | "staff";
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface KpiMetric {
  value?: number | null;
  formatted_value: string;
  change_value?: number | null;
  change_percentage?: number | null;
  trend_direction: "up" | "down" | "neutral";
  comparison_label: string;
}

export interface AtRiskMemberItem {
  member_id: string;
  name: string;
  email: string;
  phone: string;
  risk_reason: string;
  membership_id?: string | null;
  expiry_date?: string | null;
  days_remaining?: number | null;
  failed_payment_amount?: number | null;
}

export interface HistoricalMetricPoint {
  metric_date: string;
  active_members: number;
  mrr: number;
  renewal_rate?: number | null;
  at_risk_count: number;
}

export interface PlanDistributionItem {
  plan_name: string;
  active_count: number;
  mrr_contribution: number;
}

export interface DashboardSummaryResponse {
  gym_id: string;
  gym_name: string;
  metric_date: string;
  has_data: boolean;
  active_members: KpiMetric;
  mrr: KpiMetric;
  renewal_rate: KpiMetric;
  at_risk_members: KpiMetric;
  at_risk_list: AtRiskMemberItem[];
  history: HistoricalMetricPoint[];
  plan_distribution: PlanDistributionItem[];
}

export interface Member {
  id: string;
  gym_id: string;
  name: string;
  first_name?: string | null;
  last_name?: string | null;
  email: string;
  phone: string;
  date_of_birth?: string | null;
  age?: number | null;
  gender?: string | null;
  occupation?: string | null;
  city?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  join_date: string;
  preferred_training_time?: string | null;
  fitness_goal?: string | null;
  acquisition_source?: string | null;
  referral_source?: string | null;
  trainer_id?: string | null;
  trainer_name?: string | null;
  status: "active" | "inactive";
  membership_plan_name?: string | null;
  membership_end_date?: string | null;
  membership_status?: string | null;
  lifetime_value?: number;
  total_payments?: number;
  last_payment_date?: string | null;
  renewal_count?: number;
  created_at: string;
}

export interface MemberListResponse {
  items: Member[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface MembershipPlan {
  id: string;
  gym_id: string;
  name: string;
  price: number;
  duration_days: number;
  created_at: string;
}

export interface MembershipPlanListResponse {
  items: MembershipPlan[];
  total: number;
}

export interface Membership {
  id: string;
  gym_id: string;
  member_id: string;
  member_name?: string | null;
  member_email?: string | null;
  plan_id: string;
  plan_name?: string | null;
  plan_price?: number | null;
  plan_duration_days?: number | null;
  start_date: string;
  end_date: string;
  status: "active" | "expired" | "cancelled";
  created_at: string;
}

export interface MembershipListResponse {
  items: Membership[];
  total: number;
}

export interface Payment {
  id: string;
  gym_id: string;
  member_id: string;
  member_name?: string | null;
  member_email?: string | null;
  membership_id?: string | null;
  plan_name?: string | null;
  amount: number;
  paid_at: string;
  status: "paid" | "failed" | "refunded" | "success";
}

export interface PaymentListResponse {
  items: Payment[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Trainer {
  id: string;
  gym_id: string;
  user_id?: string | null;
  name: string;
  email: string;
  phone?: string | null;
  specialty: string;
  years_of_experience: number;
  certification?: string | null;
  certification_level?: string | null;
  joining_date?: string | null;
  employment_type: string;
  status: "active" | "inactive";
  max_client_capacity: number;
  rating: number;
  assigned_clients_count?: number;
  client_load_percent?: number;
  revenue_generated?: number;
  retention_rate?: number | null;
  created_at: string;
}

export interface TrainerListResponse {
  items: Trainer[];
  total: number;
}

// ============================================================
// Analytics BI Interfaces
// ============================================================
export interface OverviewKpiItem {
  value?: number | null;
  formatted_value: string;
  trend_percent?: number | null;
  trend_direction: "up" | "down" | "neutral";
  subtext?: string | null;
}

export interface AnalyticsOverviewResponse {
  total_members: OverviewKpiItem;
  active_members: OverviewKpiItem;
  active_percent: OverviewKpiItem;
  mrr: OverviewKpiItem;
  renewal_rate: OverviewKpiItem;
  at_risk_members: OverviewKpiItem;
  has_data: boolean;
}

export interface MemberSegmentItem {
  segment_name: string;
  count: number;
  percent: number;
  description: string;
}

export interface MemberIntelligenceResponse {
  total_members: number;
  active_members: number;
  inactive_members: number;
  new_this_month: number;
  expiring_soon_count: number;
  at_risk_count: number;
  avg_age?: number | null;
  avg_membership_duration_days?: number | null;
  avg_lifetime_value: number;
  arpu: number;
  renewal_rate?: number | null;
  churn_rate: number;
  member_growth_rate_30d: number;
  segments: MemberSegmentItem[];
}

export interface GenderDemographicItem {
  gender: string;
  count: number;
  percentage: number;
  active_count: number;
  renewal_rate?: number | null;
  avg_ltv: number;
}

export interface AgeGroupItem {
  age_group: string;
  count: number;
  percentage: number;
  active_count: number;
  revenue_contribution: number;
  renewal_rate?: number | null;
}

export interface DemographicsResponse {
  gender_distribution: GenderDemographicItem[];
  age_groups: AgeGroupItem[];
  most_represented_age_group?: string | null;
  fastest_growing_age_group?: string | null;
  total_reported_profiles: number;
}

export interface PlanRevenueItem {
  plan_name: string;
  active_count: number;
  mrr_contribution: number;
  percentage_of_mrr: number;
}

export interface MonthlyRevenueItem {
  month_label: string;
  amount: number;
  transaction_count: number;
}

export interface RevenueIntelligenceResponse {
  mrr: number;
  total_revenue_all_time: number;
  revenue_this_month: number;
  revenue_previous_month: number;
  arpu: number;
  avg_transaction_value: number;
  plan_breakdown: PlanRevenueItem[];
  monthly_trend: MonthlyRevenueItem[];
  revenue_by_gender: Array<{ gender: string; revenue: number }>;
  revenue_by_age_group: Array<{ age_group: string; revenue: number }>;
}

export interface FunnelStage {
  stage: string;
  count: number;
  percentage_of_total: number;
}

export interface MembershipIntelligenceResponse {
  active_count: number;
  expired_count: number;
  expiring_7d_count: number;
  expiring_30d_count: number;
  new_this_month_count: number;
  renewed_this_month_count: number;
  cancelled_count: number;
  renewal_rate?: number | null;
  churn_rate: number;
  avg_plan_duration_days: number;
  lifecycle_funnel: FunnelStage[];
}

export interface TrainerPerformanceItem {
  trainer_id: string;
  name: string;
  specialty: string;
  status: string;
  rating: number;
  assigned_members: number;
  max_capacity: number;
  utilization_percent: number;
  revenue_generated: number;
  retention_rate?: number | null;
}

export interface TrainerIntelligenceResponse {
  total_trainers: number;
  active_trainers: number;
  avg_members_per_trainer: number;
  overall_utilization_percent: number;
  trainers: TrainerPerformanceItem[];
  specialization_distribution: Array<{ specialty: string; count: number }>;
}

export interface ForecastMetric {
  metric_name: string;
  current_value: number;
  projected_next_month?: number | null;
  projected_growth_percent?: number | null;
  methodology: string;
  confidence_note: string;
}

export interface ForecastResponse {
  has_sufficient_history: boolean;
  status_message: string;
  projection_date: string;
  projected_members: ForecastMetric;
  projected_mrr: ForecastMetric;
  projected_renewals: ForecastMetric;
  projected_churn: ForecastMetric;
}

export interface InsightItem {
  id: string;
  type: "descriptive" | "diagnostic" | "forecasting" | "actionable";
  category: "demographics" | "revenue" | "retention" | "trainers" | "plans";
  title: string;
  message: string;
  metric_context?: string | null;
  recommendation?: string | null;
  severity: "info" | "warning" | "success";
}

export interface InsightsResponse {
  insights: InsightItem[];
  generated_at: string;
}
