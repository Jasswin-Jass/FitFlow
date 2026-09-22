import React from "react";
import { Card } from "@/components/ui/card";
import { TrendBadge } from "@/components/trend-badge";
import { Skeleton } from "@/components/ui/skeleton";

export interface KpiCardMetric {
  value?: number | null;
  formatted_value: string;
  change_value?: number | null;
  change_percentage?: number | null;
  trend_percent?: number | null;
  trend_direction: "up" | "down" | "neutral";
  comparison_label?: string | null;
  subtext?: string | null;
}

interface KpiCardProps {
  title: string;
  metric?: KpiCardMetric | null;
  icon: React.ElementType;
  isLoading?: boolean;
}

export function KpiCard({ title, metric, icon: Icon, isLoading }: KpiCardProps) {
  if (isLoading || !metric) {
    return (
      <Card className="border-zinc-800 bg-zinc-900/60 p-5">
        <div className="flex items-center justify-between mb-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-8 rounded-lg" />
        </div>
        <Skeleton className="h-8 w-28 mb-2" />
        <Skeleton className="h-3 w-36" />
      </Card>
    );
  }

  const label =
    metric.trend_percent !== null && metric.trend_percent !== undefined
      ? `${metric.trend_percent > 0 ? "+" : ""}${metric.trend_percent}%`
      : metric.change_percentage !== null && metric.change_percentage !== undefined
      ? `${metric.change_percentage > 0 ? "+" : ""}${metric.change_percentage}%`
      : metric.change_value !== null && metric.change_value !== undefined
      ? `${metric.change_value > 0 ? "+" : ""}${metric.change_value}`
      : null;

  const comparison = metric.subtext || metric.comparison_label || "";

  return (
    <Card className="border-zinc-800 bg-zinc-900/70 p-5 transition-all hover:border-zinc-700/80 hover:bg-zinc-900/90 shadow-sm flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
            {title}
          </span>
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-800/80 text-zinc-300">
            <Icon className="h-3.5 w-3.5" />
          </div>
        </div>

        <div className="flex items-baseline gap-2 mb-2">
          <div className="text-2xl font-bold tracking-tight text-white font-mono">
            {metric.formatted_value}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1.5 flex-wrap">
        {label && <TrendBadge direction={metric.trend_direction} label={label} />}
        {comparison && (
          <span className="text-[11px] text-zinc-400 truncate">
            {comparison}
          </span>
        )}
      </div>
    </Card>
  );
}
