"use client";

import React from "react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { DemographicsResponse } from "@/types/api";
import { Users, PieChart as PieIcon, BarChart2 } from "lucide-react";

interface DemographicsOverviewProps {
  data?: DemographicsResponse;
  isLoading?: boolean;
}

const GENDER_COLORS: Record<string, string> = {
  Male: "#3b82f6",
  Female: "#ec4899",
  Other: "#a855f7",
  "Prefer not to say": "#64748b",
  "Not Specified": "#52525b",
};

export function DemographicsOverview({ data, isLoading }: DemographicsOverviewProps) {
  if (isLoading || !data) {
    return (
      <Card className="border-zinc-800 bg-zinc-900/70 p-6">
        <div className="h-48 flex items-center justify-center text-xs text-zinc-500">
          Loading demographics intelligence...
        </div>
      </Card>
    );
  }

  const genderData = data.gender_distribution.map((g) => ({
    name: g.gender,
    value: g.count,
    percentage: g.percentage,
    color: GENDER_COLORS[g.gender] || "#6366f1",
  }));

  const ageData = data.age_groups.map((a) => ({
    name: a.age_group,
    count: a.count,
    active: a.active_count,
    rev: a.revenue_contribution,
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* 1. Gender Distribution Donut */}
      <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm flex flex-col justify-between">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <PieIcon className="h-4 w-4 text-indigo-400" />
              <CardTitle className="text-sm font-semibold text-white">
                Gender Demographics
              </CardTitle>
            </div>
            <span className="text-[11px] font-mono text-zinc-400">
              {data.total_reported_profiles} profiles
            </span>
          </div>
          <CardDescription className="text-xs text-zinc-400">
            Self-reported gender distribution
          </CardDescription>
        </CardHeader>

        <CardContent className="pt-2">
          <div className="h-40 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={genderData}
                  cx="50%"
                  cy="50%"
                  innerRadius={38}
                  outerRadius={60}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {genderData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-zinc-700 bg-zinc-900 p-2 text-xs shadow-md">
                          <span className="font-semibold text-white">{item.name}: </span>
                          <span className="font-mono text-zinc-300">
                            {item.value} members ({item.percentage}%)
                          </span>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 pt-2 border-t border-zinc-800/60 text-xs">
            {genderData.map((g) => (
              <div key={g.name} className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: g.color }} />
                <span className="text-zinc-400 text-[11px]">
                  {g.name}: <strong className="text-zinc-200 font-mono">{g.value}</strong> ({g.percentage}%)
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 2. Age Groups Histogram */}
      <Card className="border-zinc-800 bg-zinc-900/70 shadow-sm flex flex-col justify-between">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart2 className="h-4 w-4 text-indigo-400" />
              <CardTitle className="text-sm font-semibold text-white">
                Age Distribution
              </CardTitle>
            </div>
            {data.most_represented_age_group && (
              <span className="text-[10px] font-medium text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/40">
                Core: {data.most_represented_age_group} yrs
              </span>
            )}
          </div>
          <CardDescription className="text-xs text-zinc-400">
            Calculated dynamic age from member date of birth
          </CardDescription>
        </CardHeader>

        <CardContent className="pt-2">
          <div className="h-40 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ageData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#71717a" fontSize={10} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={10} tickLine={false} allowDecimals={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-zinc-700 bg-zinc-900 p-2 text-xs shadow-md">
                          <p className="font-semibold text-white">Age {item.name}</p>
                          <p className="text-zinc-300">Total Members: <span className="font-mono text-indigo-400">{item.count}</span></p>
                          <p className="text-zinc-300">Active Members: <span className="font-mono text-emerald-400">{item.active}</span></p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-2 border-t border-zinc-800/60 flex items-center justify-between text-[11px] text-zinc-400">
            <span>Fastest growing cohort: <strong className="text-zinc-200">{data.fastest_growing_age_group || "25-34"}</strong></span>
            <span>Total analyzed: <strong className="text-zinc-200 font-mono">{data.total_reported_profiles}</strong></span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
