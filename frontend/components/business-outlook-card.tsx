"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { ForecastResponse } from "@/types/api";
import { formatINR } from "@/lib/utils";
import { Sparkles, TrendingUp, RefreshCw, UserMinus, ShieldAlert } from "lucide-react";

interface BusinessOutlookCardProps {
  data?: ForecastResponse;
  isLoading?: boolean;
}

export function BusinessOutlookCard({ data, isLoading }: BusinessOutlookCardProps) {
  if (isLoading || !data) {
    return (
      <Card className="border-zinc-800 bg-zinc-900/70 p-6">
        <div className="h-32 flex items-center justify-center text-xs text-zinc-500">
          Computing trend-based business projections...
        </div>
      </Card>
    );
  }

  if (!data.has_sufficient_history) {
    return (
      <Card className="border-zinc-800 bg-zinc-900/70 p-6">
        <div className="flex items-center gap-3 text-amber-400">
          <ShieldAlert className="h-5 w-5 shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-white">Business Outlook Status</h4>
            <p className="text-xs text-zinc-400 mt-0.5">{data.status_message}</p>
          </div>
        </div>
      </Card>
    );
  }

  const { projected_members, projected_mrr, projected_renewals, projected_churn } = data;

  return (
    <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900/90 via-zinc-900/70 to-indigo-950/20 shadow-md">
      <CardHeader className="pb-3 border-b border-zinc-800/60">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-indigo-600/30 text-indigo-400 border border-indigo-500/30">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-base font-semibold text-white">
                Business Outlook (Next 30 Days)
              </CardTitle>
              <CardDescription className="text-xs text-zinc-400">
                Transparent statistical forecast derived from historical trajectory
              </CardDescription>
            </div>
          </div>
          <span className="text-[11px] font-mono text-zinc-400 bg-zinc-800/80 px-2.5 py-1 rounded-md border border-zinc-700/60 self-start sm:self-auto">
            Target: {data.projection_date}
          </span>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 1. Projected Active Members */}
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-950/50 p-4">
            <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
              <span>Projected Members</span>
              <TrendingUp className="h-3.5 w-3.5 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {projected_members.projected_next_month ?? "N/A"}
            </div>
            <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
              <span>{projected_members.projected_growth_percent != null ? `${projected_members.projected_growth_percent > 0 ? "+" : ""}${projected_members.projected_growth_percent}%` : "—"}</span>
              <span className="text-zinc-500">projected growth</span>
            </p>
          </div>

          {/* 2. Projected MRR */}
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-950/50 p-4">
            <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
              <span>Projected MRR</span>
              <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {projected_mrr.projected_next_month != null
                ? formatINR(projected_mrr.projected_next_month)
                : "N/A"}
            </div>
            <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
              <span>{projected_mrr.projected_growth_percent != null ? `${projected_mrr.projected_growth_percent > 0 ? "+" : ""}${projected_mrr.projected_growth_percent}%` : "—"}</span>
              <span className="text-zinc-500">projected trajectory</span>
            </p>
          </div>

          {/* 3. Expected Renewals */}
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-950/50 p-4">
            <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
              <span>Expected Renewals</span>
              <RefreshCw className="h-3.5 w-3.5 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {projected_renewals.projected_next_month ?? "0"}
            </div>
            <p className="text-[11px] text-zinc-400 mt-1 truncate">
              {projected_renewals.confidence_note}
            </p>
          </div>

          {/* 4. Expected Churn */}
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-950/50 p-4">
            <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
              <span>Expected Churn</span>
              <UserMinus className="h-3.5 w-3.5 text-amber-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              ~{projected_churn.projected_next_month ?? "0"}
            </div>
            <p className="text-[11px] text-zinc-400 mt-1 truncate">
              {projected_churn.confidence_note}
            </p>
          </div>
        </div>

        {/* Methodology Disclosure */}
        <div className="rounded-lg bg-zinc-950/60 p-3 border border-zinc-800/60 text-xs text-zinc-400 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <p>
            <strong className="text-zinc-200">Methodology: </strong>
            {projected_members.methodology}
          </p>
          <span className="text-[10px] uppercase font-mono tracking-wider text-indigo-400 shrink-0 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-900/60">
            Trend-based projection
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
