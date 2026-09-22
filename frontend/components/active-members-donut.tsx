"use client";

import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Users2 } from "lucide-react";

interface ActiveMembersDonutProps {
  total: number;
  active: number;
  inactive: number;
  expiringSoon: number;
}

const COLORS = ["#6366f1", "#eab308", "#71717a"];

export function ActiveMembersDonut({
  total,
  active,
  inactive,
  expiringSoon,
}: ActiveMembersDonutProps) {
  const activeHealthy = Math.max(0, active - expiringSoon);
  const data = [
    { name: "Active (Healthy)", value: activeHealthy, color: "#6366f1" },
    { name: "Expiring Soon", value: expiringSoon, color: "#eab308" },
    { name: "Inactive / Expired", value: inactive, color: "#52525b" },
  ].filter((d) => d.value > 0);

  const activePercent = total > 0 ? Math.round((active / total) * 100) : 0;

  return (
    <Card className="border-zinc-800 bg-zinc-900/70 flex flex-col justify-between shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users2 className="h-4 w-4 text-indigo-400" />
            <CardTitle className="text-base font-semibold text-white">
              Member Status Health
            </CardTitle>
          </div>
          <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950/60 px-2 py-0.5 rounded-full border border-indigo-800/40">
            {activePercent}% Active
          </span>
        </div>
        <CardDescription className="text-xs text-zinc-400">
          Distribution of {total} registered member profiles
        </CardDescription>
      </CardHeader>

      <CardContent className="flex flex-col items-center justify-center pt-2">
        <div className="relative h-44 w-full flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                innerRadius={50}
                outerRadius={70}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const item = payload[0];
                    return (
                      <div className="rounded-lg border border-zinc-700 bg-zinc-900 p-2 text-xs shadow-md">
                        <span className="font-semibold text-white">{item.name}: </span>
                        <span className="font-mono text-indigo-400">{item.value} members</span>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>

          {/* Center Callout */}
          <div className="absolute flex flex-col items-center justify-center pointer-events-none">
            <span className="text-2xl font-bold font-mono text-white">{active}</span>
            <span className="text-[10px] uppercase font-semibold text-zinc-400">
              Active / {total}
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="w-full grid grid-cols-3 gap-2 pt-3 border-t border-zinc-800/60 text-center text-xs">
          <div>
            <div className="flex items-center justify-center gap-1.5 text-zinc-400">
              <span className="h-2 w-2 rounded-full bg-indigo-500" />
              <span>Healthy</span>
            </div>
            <p className="font-mono font-semibold text-zinc-200 mt-0.5">{activeHealthy}</p>
          </div>
          <div>
            <div className="flex items-center justify-center gap-1.5 text-zinc-400">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              <span>Expiring</span>
            </div>
            <p className="font-mono font-semibold text-zinc-200 mt-0.5">{expiringSoon}</p>
          </div>
          <div>
            <div className="flex items-center justify-center gap-1.5 text-zinc-400">
              <span className="h-2 w-2 rounded-full bg-zinc-600" />
              <span>Inactive</span>
            </div>
            <p className="font-mono font-semibold text-zinc-200 mt-0.5">{inactive}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
