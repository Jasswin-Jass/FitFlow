import React from "react";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface TrendBadgeProps {
  direction: "up" | "down" | "neutral";
  label?: string | null;
  className?: string;
}

export function TrendBadge({ direction, label, className }: TrendBadgeProps) {
  if (!label) return null;

  const colorStyles = {
    up: "bg-emerald-950/60 text-emerald-400 border border-emerald-800/40",
    down: "bg-red-950/60 text-red-400 border border-red-800/40",
    neutral: "bg-zinc-800/60 text-zinc-400 border border-zinc-700/40",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
        colorStyles[direction],
        className
      )}
    >
      {direction === "up" && <ArrowUpRight className="h-3.5 w-3.5 shrink-0" />}
      {direction === "down" && <ArrowDownRight className="h-3.5 w-3.5 shrink-0" />}
      {direction === "neutral" && <Minus className="h-3 w-3 shrink-0" />}
      <span>{label}</span>
    </div>
  );
}
