"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { InsightItem } from "@/types/api";
import { Lightbulb, Info, AlertTriangle, CheckCircle2, ArrowRight } from "lucide-react";

interface ActionableInsightsGridProps {
  insights?: InsightItem[];
  isLoading?: boolean;
}

export function ActionableInsightsGrid({
  insights,
  isLoading,
}: ActionableInsightsGridProps) {
  if (isLoading) {
    return (
      <Card className="border-zinc-800 bg-zinc-900/70 p-6">
        <div className="h-32 flex items-center justify-center text-xs text-zinc-500">
          Synthesizing data-backed gym insights...
        </div>
      </Card>
    );
  }

  if (!insights || insights.length === 0) {
    return null;
  }

  const typeBadges: Record<string, { label: string; color: string }> = {
    descriptive: { label: "Descriptive", color: "bg-blue-950/60 text-blue-400 border-blue-800/40" },
    diagnostic: { label: "Diagnostic", color: "bg-purple-950/60 text-purple-400 border-purple-800/40" },
    forecasting: { label: "Forecasting", color: "bg-indigo-950/60 text-indigo-400 border-indigo-800/40" },
    actionable: { label: "Actionable", color: "bg-emerald-950/60 text-emerald-400 border-emerald-800/40" },
  };

  return (
    <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm">
      <CardHeader className="pb-3 border-b border-zinc-800/60">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-amber-400" />
            <CardTitle className="text-base font-semibold text-white">
              Data-Driven Business Insights
            </CardTitle>
          </div>
          <span className="text-[11px] font-mono text-zinc-400">
            {insights.length} active observations
          </span>
        </div>
        <CardDescription className="text-xs text-zinc-400">
          Automated pattern discovery derived from operational records and member metrics
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((item) => {
            const badge = typeBadges[item.type] || typeBadges.descriptive;
            return (
              <div
                key={item.id}
                className="flex flex-col justify-between rounded-lg border border-zinc-800 bg-zinc-950/60 p-4 space-y-3 transition-colors hover:border-zinc-700/80"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`text-[10px] font-mono uppercase font-semibold px-2 py-0.5 rounded border ${badge.color}`}
                    >
                      {badge.label}
                    </span>
                    <span className="text-[10px] uppercase font-semibold tracking-wider text-zinc-400 capitalize">
                      {item.category}
                    </span>
                  </div>

                  <h4 className="text-sm font-semibold text-zinc-100">{item.title}</h4>
                  <p className="text-xs text-zinc-300 leading-relaxed">{item.message}</p>

                  {item.metric_context && (
                    <div className="rounded bg-zinc-900/80 px-2.5 py-1 text-[11px] font-mono text-indigo-300 border border-zinc-800">
                      Context: {item.metric_context}
                    </div>
                  )}
                </div>

                {item.recommendation && (
                  <div className="pt-2 border-t border-zinc-800/60">
                    <p className="text-xs text-emerald-400/90 flex items-start gap-1.5">
                      <ArrowRight className="h-3.5 w-3.5 shrink-0 mt-0.5 text-emerald-400" />
                      <span>{item.recommendation}</span>
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
