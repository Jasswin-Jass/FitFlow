"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { DashboardSummaryResponse } from "@/types/api";

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => api.get<DashboardSummaryResponse>("/dashboard/summary"),
    staleTime: 30 * 1000,
  });
}

export function useRecomputeMetrics() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      api.post<DashboardSummaryResponse>("/admin/recompute-metrics"),
    onSuccess: (data) => {
      queryClient.setQueryData(["dashboard-summary"], data);
      toast.success("Metrics recomputed successfully!", {
        description: `Active members: ${data.active_members.formatted_value} | MRR: ${data.mrr.formatted_value}`,
      });
    },
    onError: (err: any) => {
      toast.error("Failed to recompute metrics", {
        description: err.detail || err.message,
      });
    },
  });
}
