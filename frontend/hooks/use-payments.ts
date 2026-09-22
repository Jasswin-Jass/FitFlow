"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { Payment, PaymentListResponse } from "@/types/api";

export function usePayments(params?: {
  status?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: ["payments", params],
    queryFn: () =>
      api.get<PaymentListResponse>("/payments", {
        status: params?.status === "all" ? undefined : params?.status,
        start_date: params?.start_date || undefined,
        end_date: params?.end_date || undefined,
        page: params?.page || 1,
        size: params?.size || 20,
      }),
  });
}

export function useCreatePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      member_id: string;
      membership_id?: string;
      amount: number;
      status?: "success" | "failed" | "refunded";
      paid_at?: string;
    }) => api.post<Payment>("/payments", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Payment recorded successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to record payment", {
        description: err.detail || err.message,
      });
    },
  });
}
