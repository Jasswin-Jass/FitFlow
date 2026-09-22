"use client";

import React, { useState } from "react";
import {
  Users,
  LineChart,
  PieChart as PieIcon,
  BarChart2,
  TrendingUp,
  Dumbbell,
  Lightbulb,
  Calendar,
  Filter,
  ArrowRight,
  ShieldAlert,
  Percent,
  IndianRupee,
  RefreshCw,
  Sparkles,
  AlertTriangle,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  Line,
  AreaChart,
  Area,
} from "recharts";
import { Header } from "@/components/header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  useMemberIntelligence,
  useDemographics,
  useRevenueIntelligence,
  useMembershipIntelligence,
  useTrainerIntelligence,
  useForecast,
  useActionableInsights,
} from "@/hooks/use-analytics";
import { formatINR } from "@/lib/utils";

const TABS = [
  { id: "members", label: "Member Intelligence", icon: Users },
  { id: "demographics", label: "Demographics", icon: PieIcon },
  { id: "revenue", label: "Revenue Intelligence", icon: IndianRupee },
  { id: "memberships", label: "Membership Lifecycle", icon: RefreshCw },
  { id: "trainers", label: "Trainer Intelligence", icon: Dumbbell },
  { id: "outlook", label: "Outlook & Insights", icon: Sparkles },
];

const GENDER_COLORS: Record<string, string> = {
  Male: "#3b82f6",
  Female: "#ec4899",
  Other: "#a855f7",
  "Prefer not to say": "#64748b",
  "Not Specified": "#52525b",
};

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState("members");
  const [dateRange, setDateRange] = useState("30d");

  // Fetch all intelligence queries
  const { data: memberIntel, isLoading: isMemLoading } = useMemberIntelligence();
  const { data: demo, isLoading: isDemoLoading } = useDemographics();
  const { data: revIntel, isLoading: isRevLoading } = useRevenueIntelligence();
  const { data: mshipIntel, isLoading: isMshipLoading } = useMembershipIntelligence();
  const { data: trainerIntel, isLoading: isTrainerLoading } = useTrainerIntelligence();
  const { data: forecast, isLoading: isForecastLoading } = useForecast();
  const { data: insightsData, isLoading: isInsightsLoading } = useActionableInsights();

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Deep-Dive Business Intelligence"
        subtitle="Granular analysis across member demographics, revenue drivers, trainer performance, and statistical outlook"
        showRecompute={true}
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Filter & Tab Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
          {/* Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 bg-zinc-900/60 p-1 rounded-lg border border-zinc-800/80">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* Time Window Filter */}
          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs text-zinc-400 flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5 text-zinc-500" /> Window:
            </span>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="h-8 rounded-md border border-zinc-700/60 bg-zinc-900 px-2.5 text-xs text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="30d">Last 30 Days</option>
              <option value="60d">Last 60 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="all">All Available History</option>
            </select>
          </div>
        </div>

        {/* ========================================================= */}
        {/* TAB 1: MEMBER INTELLIGENCE */}
        {/* ========================================================= */}
        {activeTab === "members" && (
          <div className="space-y-6">
            {/* KPI Metrics Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
                <span className="text-[11px] uppercase tracking-wider text-zinc-400">Total Members</span>
                <p className="text-xl font-bold font-mono text-white mt-1">{memberIntel?.total_members ?? "—"}</p>
                <span className="text-[10px] text-zinc-400">All registered profiles</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
                <span className="text-[11px] uppercase tracking-wider text-zinc-400">Active Core</span>
                <p className="text-xl font-bold font-mono text-emerald-400 mt-1">{memberIntel?.active_members ?? "—"}</p>
                <span className="text-[10px] text-zinc-400">Paid memberships</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
                <span className="text-[11px] uppercase tracking-wider text-zinc-400">Average Age</span>
                <p className="text-xl font-bold font-mono text-white mt-1">{memberIntel?.avg_age ? `${memberIntel.avg_age} yrs` : "N/A"}</p>
                <span className="text-[10px] text-zinc-400">Dynamic from DOB</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
                <span className="text-[11px] uppercase tracking-wider text-zinc-400">Average LTV</span>
                <p className="text-xl font-bold font-mono text-indigo-400 mt-1">{memberIntel ? formatINR(memberIntel.avg_lifetime_value) : "—"}</p>
                <span className="text-[10px] text-zinc-400">Revenue per profile</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
                <span className="text-[11px] uppercase tracking-wider text-zinc-400">ARPU</span>
                <p className="text-xl font-bold font-mono text-indigo-400 mt-1">{memberIntel ? formatINR(memberIntel.arpu) : "—"}</p>
                <span className="text-[10px] text-zinc-400">MRR / Active member</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
                <span className="text-[11px] uppercase tracking-wider text-zinc-400">30d Growth</span>
                <p className="text-xl font-bold font-mono text-emerald-400 mt-1">
                  {memberIntel ? `${memberIntel.member_growth_rate_30d > 0 ? "+" : ""}${memberIntel.member_growth_rate_30d}%` : "—"}
                </p>
                <span className="text-[10px] text-zinc-400">Net member expansion</span>
              </div>
            </div>

            {/* Segmentation Analysis Table */}
            <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
              <CardHeader className="pb-3 border-b border-zinc-800/60">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-indigo-400" />
                    <CardTitle className="text-base font-semibold text-white">
                      Rule-Based Member Segmentation
                    </CardTitle>
                  </div>
                  <span className="text-xs text-zinc-400">Deterministic criteria</span>
                </div>
                <CardDescription className="text-xs text-zinc-400">
                  Transparent member categorization based on operational status, spend, and renewal timing
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-zinc-800 text-zinc-400">
                        <th className="pb-2 font-medium">Segment Name</th>
                        <th className="pb-2 font-medium">Members</th>
                        <th className="pb-2 font-medium">Share %</th>
                        <th className="pb-2 font-medium">Transparent Definition</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                      {memberIntel?.segments.map((seg) => (
                        <tr key={seg.segment_name} className="hover:bg-zinc-800/30">
                          <td className="py-2.5 font-semibold text-zinc-200">{seg.segment_name}</td>
                          <td className="py-2.5 font-mono text-white font-bold">{seg.count}</td>
                          <td className="py-2.5 font-mono text-indigo-400">{seg.percent}%</td>
                          <td className="py-2.5 text-zinc-400">{seg.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 2: DEMOGRAPHICS */}
        {/* ========================================================= */}
        {activeTab === "demographics" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Gender Chart & Table */}
              <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
                <CardHeader className="pb-3 border-b border-zinc-800/60">
                  <CardTitle className="text-base font-semibold text-white">
                    Gender Distribution & Retention
                  </CardTitle>
                  <CardDescription className="text-xs text-zinc-400">
                    Self-reported member profiles and cross-sectional spend
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
                  <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={demo?.gender_distribution.map((g) => ({
                            name: g.gender,
                            value: g.count,
                            color: GENDER_COLORS[g.gender] || "#6366f1",
                          }))}
                          cx="50%"
                          cy="50%"
                          innerRadius={45}
                          outerRadius={75}
                          paddingAngle={3}
                          dataKey="value"
                          stroke="none"
                        >
                          {demo?.gender_distribution.map((g) => (
                            <Cell key={g.gender} fill={GENDER_COLORS[g.gender] || "#6366f1"} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-zinc-800 text-zinc-400">
                          <th className="pb-1.5 font-medium">Gender</th>
                          <th className="pb-1.5 font-medium">Count</th>
                          <th className="pb-1.5 font-medium">Share</th>
                          <th className="pb-1.5 font-medium">Active</th>
                          <th className="pb-1.5 font-medium">Avg LTV</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-zinc-800/50">
                        {demo?.gender_distribution.map((g) => (
                          <tr key={g.gender}>
                            <td className="py-2 text-zinc-200 font-medium flex items-center gap-1.5">
                              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: GENDER_COLORS[g.gender] || "#6366f1" }} />
                              {g.gender}
                            </td>
                            <td className="py-2 font-mono text-white font-bold">{g.count}</td>
                            <td className="py-2 font-mono text-indigo-400">{g.percentage}%</td>
                            <td className="py-2 font-mono text-emerald-400">{g.active_count}</td>
                            <td className="py-2 font-mono text-zinc-300">{formatINR(g.avg_ltv)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {/* Age Group Analysis */}
              <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
                <CardHeader className="pb-3 border-b border-zinc-800/60">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-semibold text-white">
                      Age Category Breakdown
                    </CardTitle>
                    {demo?.most_represented_age_group && (
                      <Badge variant="secondary" className="text-xs">
                        Dominant: {demo.most_represented_age_group}
                      </Badge>
                    )}
                  </div>
                  <CardDescription className="text-xs text-zinc-400">
                    Distribution and cumulative revenue across age cohorts
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
                  <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={demo?.age_groups} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <XAxis dataKey="age_group" stroke="#71717a" fontSize={11} tickLine={false} />
                        <YAxis stroke="#71717a" fontSize={11} tickLine={false} allowDecimals={false} />
                        <Tooltip />
                        <Bar dataKey="count" fill="#6366f1" name="Members" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="active_count" fill="#10b981" name="Active" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-zinc-800 text-zinc-400">
                          <th className="pb-1.5 font-medium">Age Group</th>
                          <th className="pb-1.5 font-medium">Members</th>
                          <th className="pb-1.5 font-medium">Share</th>
                          <th className="pb-1.5 font-medium">Revenue Contribution</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-zinc-800/50">
                        {demo?.age_groups.map((a) => (
                          <tr key={a.age_group}>
                            <td className="py-2 text-zinc-200 font-semibold">{a.age_group}</td>
                            <td className="py-2 font-mono text-white font-bold">{a.count}</td>
                            <td className="py-2 font-mono text-indigo-400">{a.percentage}%</td>
                            <td className="py-2 font-mono text-emerald-400">{formatINR(a.revenue_contribution)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 3: REVENUE INTELLIGENCE */}
        {/* ========================================================= */}
        {activeTab === "revenue" && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Total All-Time</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">
                  {revIntel ? formatINR(revIntel.total_revenue_all_time) : "—"}
                </p>
                <span className="text-[11px] text-zinc-400">Cumulative collected cash</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Current Month</span>
                <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                  {revIntel ? formatINR(revIntel.revenue_this_month) : "—"}
                </p>
                <span className="text-[11px] text-zinc-400">Paid in current cycle</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Monthly Recurring</span>
                <p className="text-2xl font-bold font-mono text-indigo-400 mt-1">
                  {revIntel ? formatINR(revIntel.mrr) : "—"}
                </p>
                <span className="text-[11px] text-zinc-400">Normalized 30-day baseline</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Avg Transaction</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">
                  {revIntel ? formatINR(revIntel.avg_transaction_value) : "—"}
                </p>
                <span className="text-[11px] text-zinc-400">Per payment logged</span>
              </div>
            </div>

            {/* Monthly Trend Bar Chart */}
            <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
              <CardHeader className="pb-3 border-b border-zinc-800/60">
                <CardTitle className="text-base font-semibold text-white">
                  6-Month Revenue Trajectory
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400">
                  Monthly cash collection aggregated from completed payment transactions
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={revIntel?.monthly_trend} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                      <XAxis dataKey="month_label" stroke="#71717a" fontSize={11} tickLine={false} />
                      <YAxis stroke="#71717a" fontSize={11} tickLine={false} tickFormatter={(val) => `₹${val / 1000}k`} />
                      <Tooltip formatter={(value: any) => [formatINR(Number(value)), "Revenue"]} />
                      <Bar dataKey="amount" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Plan Breakdown */}
            <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
              <CardHeader className="pb-3 border-b border-zinc-800/60">
                <CardTitle className="text-base font-semibold text-white">
                  Plan Contribution Breakdown
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400">
                  Active memberships and MRR share per plan
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {revIntel?.plan_breakdown.map((p) => (
                    <div key={p.plan_name} className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-zinc-200">{p.plan_name}</span>
                        <span className="font-mono text-indigo-400 font-bold">{p.percentage_of_mrr}%</span>
                      </div>
                      <p className="text-xl font-bold font-mono text-white">{formatINR(p.mrr_contribution)}/mo</p>
                      <p className="text-xs text-zinc-400">{p.active_count} active members</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 4: MEMBERSHIP LIFECYCLE */}
        {/* ========================================================= */}
        {activeTab === "memberships" && (
          <div className="space-y-6">
            <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
              <CardHeader className="pb-3 border-b border-zinc-800/60">
                <CardTitle className="text-base font-semibold text-white">
                  Membership Funnel Progression
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400">
                  Flow from creation through active retention, renewal, or lapse
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6 space-y-4">
                <div className="space-y-3">
                  {mshipIntel?.lifecycle_funnel.map((stage, idx) => (
                    <div key={stage.stage} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-zinc-200 flex items-center gap-2">
                          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-zinc-800 text-[10px] font-mono text-zinc-400">
                            {idx + 1}
                          </span>
                          {stage.stage}
                        </span>
                        <span className="font-mono text-zinc-300">
                          {stage.count} ({stage.percentage_of_total}%)
                        </span>
                      </div>
                      <div className="h-3 w-full rounded-full bg-zinc-800/80 overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full transition-all duration-700"
                          style={{ width: `${stage.percentage_of_total}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Renewal Rate</span>
                <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                  {mshipIntel?.renewal_rate !== null && mshipIntel?.renewal_rate !== undefined
                    ? `${mshipIntel.renewal_rate}%`
                    : "N/A"}
                </p>
                <span className="text-[11px] text-zinc-400">
                  {mshipIntel?.renewal_rate !== null ? "Eligible cohort renewed" : "No renewals due in period"}
                </span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Churn Rate</span>
                <p className="text-2xl font-bold font-mono text-amber-400 mt-1">{mshipIntel?.churn_rate ?? 0}%</p>
                <span className="text-[11px] text-zinc-400">Non-renewed percentage</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Average Plan Length</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">{mshipIntel?.avg_plan_duration_days ?? 0} days</p>
                <span className="text-[11px] text-zinc-400">Weighted plan commitment</span>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 5: TRAINER INTELLIGENCE */}
        {/* ========================================================= */}
        {activeTab === "trainers" && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Active Trainers</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">{trainerIntel?.active_trainers ?? 0}</p>
                <span className="text-[11px] text-zinc-400">Of {trainerIntel?.total_trainers} on roster</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Overall Utilization</span>
                <p className="text-2xl font-bold font-mono text-indigo-400 mt-1">{trainerIntel?.overall_utilization_percent ?? 0}%</p>
                <span className="text-[11px] text-zinc-400">Client load vs capacity</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Average Clients</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">{trainerIntel?.avg_members_per_trainer ?? 0}</p>
                <span className="text-[11px] text-zinc-400">Assigned per coach</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Average Rating</span>
                <p className="text-2xl font-bold font-mono text-amber-400 mt-1">
                  {trainerIntel?.avg_trainer_rating != null ? `${trainerIntel.avg_trainer_rating.toFixed(1)} ★` : "Not rated"}
                </p>
                <span className="text-[11px] text-zinc-400">Verified member reviews</span>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
                <span className="text-xs text-zinc-400 uppercase tracking-wider">Avg Experience</span>
                <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                  {trainerIntel?.avg_trainer_experience != null ? `${trainerIntel.avg_trainer_experience.toFixed(1)} yrs` : "—"}
                </p>
                <span className="text-[11px] text-zinc-400">Coaching tenure</span>
              </div>
            </div>

            {/* Trainer Performance Table */}
            <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
              <CardHeader className="pb-3 border-b border-zinc-800/60">
                <CardTitle className="text-base font-semibold text-white">
                  Trainer Workload & Revenue Contribution
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400">
                  Individual utilization, client load, and revenue generated from assigned members
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-zinc-800 text-zinc-400">
                        <th className="pb-2 font-medium">Trainer</th>
                        <th className="pb-2 font-medium">Specialty</th>
                        <th className="pb-2 font-medium">Rating</th>
                        <th className="pb-2 font-medium">Assigned</th>
                        <th className="pb-2 font-medium">Capacity</th>
                        <th className="pb-2 font-medium">Utilization</th>
                        <th className="pb-2 font-medium">Revenue Generated</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                      {trainerIntel?.trainers.map((t) => (
                        <tr key={t.trainer_id} className="hover:bg-zinc-800/30">
                          <td className="py-2.5 font-semibold text-zinc-200">{t.name}</td>
                          <td className="py-2.5 text-zinc-400">{t.specialty}</td>
                          <td className="py-2.5 font-mono text-amber-400 font-bold">
                            {t.rating != null ? (
                              `${t.rating.toFixed(1)} ★`
                            ) : (
                              <span className="text-zinc-500 font-normal italic">Not rated yet</span>
                            )}
                          </td>
                          <td className="py-2.5 font-mono text-white font-bold">{t.assigned_members}</td>
                          <td className="py-2.5 font-mono text-zinc-400">{t.max_capacity}</td>
                          <td className="py-2.5">
                            <div className="flex items-center gap-2">
                              <div className="h-2 w-16 rounded-full bg-zinc-800 overflow-hidden">
                                <div
                                  className="h-full bg-indigo-500 rounded-full"
                                  style={{ width: `${Math.min(100, t.utilization_percent)}%` }}
                                />
                              </div>
                              <span className="font-mono text-indigo-400">{t.utilization_percent}%</span>
                            </div>
                          </td>
                          <td className="py-2.5 font-mono text-emerald-400 font-semibold">{formatINR(t.revenue_generated)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 6: OUTLOOK & ACTIONABLE INSIGHTS */}
        {/* ========================================================= */}
        {activeTab === "outlook" && (
          <div className="space-y-6">
            {/* Forecast */}
            <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
              <CardHeader className="pb-3 border-b border-zinc-800/60">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-indigo-400" />
                    <CardTitle className="text-base font-semibold text-white">
                      Transparent Business Projections (30-Day Outlook)
                    </CardTitle>
                  </div>
                  <Badge variant="outline" className="text-xs font-mono">
                    Linear trend velocity
                  </Badge>
                </div>
                <CardDescription className="text-xs text-zinc-400">
                  Statistical forecasting based on 90-day moving average growth rates
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4">
                    <span className="text-xs text-zinc-400">Projected Active Members</span>
                    <p className="text-2xl font-bold font-mono text-white mt-1">
                      {forecast?.projected_members.projected_next_month ?? "—"}
                    </p>
                    <p className="text-xs text-emerald-400 mt-1">
                      {forecast?.projected_members.projected_growth_percent !== null
                        ? `${forecast?.projected_members.projected_growth_percent}% projected net growth`
                        : "—"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4">
                    <span className="text-xs text-zinc-400">Projected Monthly Revenue</span>
                    <p className="text-2xl font-bold font-mono text-white mt-1">
                      {forecast?.projected_mrr.projected_next_month
                        ? formatINR(forecast.projected_mrr.projected_next_month)
                        : "—"}
                    </p>
                    <p className="text-xs text-emerald-400 mt-1">
                      {forecast?.projected_mrr.projected_growth_percent !== null
                        ? `${forecast?.projected_mrr.projected_growth_percent}% projected trajectory`
                        : "—"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4">
                    <span className="text-xs text-zinc-400">Expected Cohort Renewals</span>
                    <p className="text-2xl font-bold font-mono text-white mt-1">
                      {forecast?.projected_renewals.projected_next_month ?? "—"}
                    </p>
                    <p className="text-xs text-zinc-400 mt-1">{forecast?.projected_renewals.confidence_note}</p>
                  </div>

                  <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4">
                    <span className="text-xs text-zinc-400">Expected Churn Buffer</span>
                    <p className="text-2xl font-bold font-mono text-white mt-1">
                      ~{forecast?.projected_churn.projected_next_month ?? "—"}
                    </p>
                    <p className="text-xs text-zinc-400 mt-1">{forecast?.projected_churn.confidence_note}</p>
                  </div>
                </div>

                <div className="rounded-lg bg-zinc-950/70 p-3.5 border border-zinc-800/80 text-xs text-zinc-300">
                  <p>
                    <strong className="text-zinc-100">Methodology: </strong>
                    {forecast?.projected_members.methodology}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Insights */}
            <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
              <CardHeader className="pb-3 border-b border-zinc-800/60">
                <CardTitle className="text-base font-semibold text-white">
                  Data-Backed Strategic Insights
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400">
                  Descriptive, diagnostic, and prescriptive observations generated from current records
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {insightsData?.insights.map((ins) => (
                    <div key={ins.id} className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4 space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800/40">
                          {ins.type}
                        </span>
                        <span className="text-[10px] uppercase text-zinc-400 capitalize">{ins.category}</span>
                      </div>
                      <h4 className="text-sm font-semibold text-zinc-100">{ins.title}</h4>
                      <p className="text-xs text-zinc-300">{ins.message}</p>
                      {ins.metric_context && (
                        <div className="rounded bg-zinc-900 px-2.5 py-1 text-[11px] font-mono text-indigo-300 border border-zinc-800">
                          {ins.metric_context}
                        </div>
                      )}
                      {ins.recommendation && (
                        <div className="pt-2 border-t border-zinc-800/60">
                          <p className="text-xs text-emerald-400 flex items-start gap-1">
                            <ArrowRight className="h-3.5 w-3.5 shrink-0 mt-0.5" />
                            <span>{ins.recommendation}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
