"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { HistoricalMetricPoint } from "@/types/api";
import { formatINR } from "@/lib/utils";

interface HistoricalChartProps {
  data: HistoricalMetricPoint[];
}

export function HistoricalChart({ data }: HistoricalChartProps) {
  const [metricMode, setMetricMode] = useState<"mrr" | "active">("mrr");

  const formattedData = data.map((point) => {
    const d = new Date(point.metric_date);
    return {
      ...point,
      displayDate: d.toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    };
  });

  return (
    <Card className="border-zinc-800 bg-zinc-900/70">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <div>
          <CardTitle className="text-base font-semibold text-white">
            30-Day Performance Trajectory
          </CardTitle>
          <CardDescription className="text-xs text-zinc-400 mt-0.5">
            Aggregated metrics tracked across daily snapshots
          </CardDescription>
        </div>

        <div className="flex items-center gap-1 rounded-lg bg-zinc-800/80 p-1">
          <button
            onClick={() => setMetricMode("mrr")}
            className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
              metricMode === "mrr"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            MRR (₹)
          </button>
          <button
            onClick={() => setMetricMode("active")}
            className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
              metricMode === "active"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            Active Members
          </button>
        </div>
      </CardHeader>

      <CardContent>
        {formattedData.length === 0 ? (
          <div className="flex h-64 items-center justify-center text-sm text-zinc-500">
            No historical metric points available yet
          </div>
        ) : (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="mrrGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="activeGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis
                  dataKey="displayDate"
                  stroke="#71717a"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="#71717a"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(val) => (metricMode === "mrr" ? formatINR(val) : String(val))}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const row = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-zinc-700 bg-zinc-950 p-2.5 shadow-xl text-xs">
                          <p className="text-zinc-400 font-medium mb-1">{row.displayDate}</p>
                          <p className="text-white font-semibold flex items-center gap-1.5">
                            <span
                              className="h-2 w-2 rounded-full"
                              style={{
                                backgroundColor: metricMode === "mrr" ? "#6366f1" : "#10b981",
                              }}
                            />
                            {metricMode === "mrr"
                              ? `MRR: ${formatINR(row.mrr)}`
                              : `Active Members: ${row.active_members}`}
                          </p>
                          <p className="text-zinc-400 mt-1">
                            Renewal Rate: {row.renewal_rate}%
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                {metricMode === "mrr" ? (
                  <Area
                    type="monotone"
                    dataKey="mrr"
                    stroke="#6366f1"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#mrrGradient)"
                  />
                ) : (
                  <Area
                    type="monotone"
                    dataKey="active_members"
                    stroke="#10b981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#activeGradient)"
                  />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
