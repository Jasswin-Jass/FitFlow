"use client";

import React from "react";
import Link from "next/link";
import {
  Users,
  UserCheck,
  Percent,
  IndianRupee,
  RefreshCw,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Layers,
  LineChart,
} from "lucide-react";
import { Header } from "@/components/header";
import { KpiCard } from "@/components/kpi-card";
import { AtRiskTable } from "@/components/at-risk-table";
import { HistoricalChart } from "@/components/historical-chart";
import { ActiveMembersDonut } from "@/components/active-members-donut";
import { DemographicsOverview } from "@/components/demographics-overview";
import { BusinessOutlookCard } from "@/components/business-outlook-card";
import { ActionableInsightsGrid } from "@/components/actionable-insights-grid";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useDashboardSummary } from "@/hooks/use-dashboard";
import {
  useAnalyticsOverview,
  useDemographics,
  useForecast,
  useActionableInsights,
  useMemberIntelligence,
} from "@/hooks/use-analytics";
import { formatINR } from "@/lib/utils";
import { PlanDistributionItem } from "@/types/api";

export default function DashboardPage() {
  const { data: summary, isLoading: isSummaryLoading } = useDashboardSummary();
  const { data: overview, isLoading: isOverviewLoading } = useAnalyticsOverview();
  const { data: demographics, isLoading: isDemoLoading } = useDemographics();
  const { data: forecast, isLoading: isForecastLoading } = useForecast();
  const { data: insightsData, isLoading: isInsightsLoading } = useActionableInsights();
  const { data: memberIntel } = useMemberIntelligence();

  const isLoading = isSummaryLoading || isOverviewLoading;

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Executive BI Overview"
        subtitle="Real-time multi-tenant business intelligence and operational performance"
        showRecompute={true}
      />

      <main className="flex-1 p-8 space-y-8">
        {/* Row 1: Top 6 Executive KPI Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <KpiCard
            title="Total Members"
            metric={overview?.total_members}
            icon={Users}
            isLoading={isLoading}
          />

          <KpiCard
            title="Active Members"
            metric={overview?.active_members}
            icon={UserCheck}
            isLoading={isLoading}
          />

          <KpiCard
            title="Active %"
            metric={overview?.active_percent}
            icon={Percent}
            isLoading={isLoading}
          />

          <KpiCard
            title="Recurring Revenue"
            metric={overview?.mrr}
            icon={IndianRupee}
            isLoading={isLoading}
          />

          <KpiCard
            title="Renewal Rate"
            metric={overview?.renewal_rate}
            icon={RefreshCw}
            isLoading={isLoading}
          />

          <KpiCard
            title="At-Risk Members"
            metric={overview?.at_risk_members}
            icon={AlertTriangle}
            isLoading={isLoading}
          />
        </div>

        {/* Zero-state notice if brand new gym */}
        {summary && !summary.has_data && (
          <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-900/40 p-8 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-950/60 text-indigo-400 mb-3">
              <TrendingUp className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-white">Welcome to FitFlow!</h3>
            <p className="text-sm text-zinc-400 max-w-md mx-auto mt-1">
              Your gym tenant environment is clean and ready. Add members and assign memberships
              to begin generating live Business Intelligence metrics.
            </p>
            <div className="flex justify-center gap-3 mt-4">
              <Link href="/members">
                <Button size="sm" className="gap-1.5">
                  Add First Member <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* Row 2: Performance Trajectory Area Chart + Active Members Donut */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <HistoricalChart data={summary?.history || []} />
          </div>

          <ActiveMembersDonut
            total={overview?.total_members?.value || 0}
            active={overview?.active_members?.value || 0}
            inactive={memberIntel?.inactive_members || 0}
            expiringSoon={memberIntel?.expiring_soon_count || 0}
          />
        </div>

        {/* Row 3: Demographics Overview + Plan Revenue Contribution */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <DemographicsOverview data={demographics} isLoading={isDemoLoading} />
          </div>

          {/* Membership Plan Revenue Distribution */}
          <Card className="border-zinc-800 bg-zinc-900/70 flex flex-col justify-between shadow-sm">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers className="h-4 w-4 text-indigo-400" />
                  <CardTitle className="text-sm font-semibold text-white">
                    Plan Distribution
                  </CardTitle>
                </div>
                <Link href="/analytics" className="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                  Deep-dive <LineChart className="h-3 w-3" />
                </Link>
              </div>
              <CardDescription className="text-xs text-zinc-400">
                Revenue & active member contribution by plan
              </CardDescription>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col justify-center">
              {!summary?.plan_distribution || summary.plan_distribution.length === 0 ? (
                <div className="text-center py-8 text-xs text-zinc-500">
                  No active memberships assigned yet.
                </div>
              ) : (
                <div className="space-y-4">
                  {summary.plan_distribution.map((item: PlanDistributionItem) => {
                    const totalMrr = summary.mrr?.value || 1;
                    const percentOfMrr = Math.min(
                      100,
                      Math.round((item.mrr_contribution / (totalMrr || 1)) * 100)
                    );

                    return (
                      <div key={item.plan_name} className="space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="font-medium text-zinc-200">
                            {item.plan_name}
                          </span>
                          <span className="text-zinc-400 font-mono text-[11px]">
                            {formatINR(item.mrr_contribution)}/mo ({item.active_count} active)
                          </span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-zinc-800 overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                            style={{ width: `${percentOfMrr}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Row 4: Business Outlook (Trend Projections) */}
        <BusinessOutlookCard data={forecast} isLoading={isForecastLoading} />

        {/* Row 5: Actionable Insights */}
        <ActionableInsightsGrid insights={insightsData?.insights} isLoading={isInsightsLoading} />

        {/* Row 6: At-Risk Action Center Table */}
        <AtRiskTable
          items={summary?.at_risk_list || []}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}
