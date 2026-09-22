"use client";

import React from "react";
import { RefreshCw, Calendar, Sparkles, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/use-auth";
import { useRecomputeMetrics } from "@/hooks/use-dashboard";

interface HeaderProps {
  title: string;
  subtitle?: string;
  showRecompute?: boolean;
}

export function Header({ title, subtitle, showRecompute = false }: HeaderProps) {
  const { user } = useAuth();
  const recomputeMutation = useRecomputeMetrics();

  const todayFormatted = new Date().toLocaleDateString("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-zinc-800/80 bg-zinc-950/80 px-8 backdrop-blur-md">
      <div>
        <h1 className="text-lg font-bold text-white tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-zinc-400">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Date Indicator */}
        <div className="hidden sm:flex items-center gap-1.5 text-xs text-zinc-400 bg-zinc-900/80 border border-zinc-800/80 px-3 py-1.5 rounded-md">
          <Calendar className="h-3.5 w-3.5 text-zinc-500" />
          <span>{todayFormatted}</span>
        </div>

        {/* Tenant Gym Indicator */}
        <div className="flex items-center gap-1.5 text-xs text-indigo-400 bg-indigo-950/40 border border-indigo-800/40 px-3 py-1.5 rounded-md">
          <Building2 className="h-3.5 w-3.5" />
          <span className="font-medium">{user?.gym_name || "FitFlow"}</span>
        </div>

        {/* Manual Recompute Button (Hero Feature) */}
        {showRecompute && user?.role === "owner" && (
          <Button
            size="sm"
            onClick={() => recomputeMutation.mutate()}
            disabled={recomputeMutation.isPending}
            className="gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs h-8 shadow-sm"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 ${
                recomputeMutation.isPending ? "animate-spin text-white" : ""
              }`}
            />
            <span>
              {recomputeMutation.isPending ? "Recomputing..." : "Recompute Metrics"}
            </span>
          </Button>
        )}
      </div>
    </header>
  );
}
