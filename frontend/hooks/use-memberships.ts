"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import {
  Membership,
  MembershipPlan,
  MembershipListResponse,
} from "@/types/api";

export function useMemberships(status?: string) {
  return useQuery({
    queryKey: ["memberships", status],
    queryFn: () =>
      api.get<MembershipListResponse>("/memberships", {
        status: status === "all" ? undefined : status,
      }),
  });
}

export function useMembershipPlans() {
  return useQuery({
    queryKey: ["membership-plans"],
    queryFn: () =>
      api.get<{ items: MembershipPlan[]; total: number }>("/membership-plans"),
  });
}

export function useCreatePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      name: string;
      description?: string;
      price: number;
      duration_days: number;
      status?: string;
    }) => api.post<MembershipPlan>("/membership-plans", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["membership-plans"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Plan created successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to create plan", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useUpdatePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<MembershipPlan>;
    }) => api.patch<MembershipPlan>(`/membership-plans/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["membership-plans"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Plan updated successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to update plan", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useDeletePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.delete(`/membership-plans/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["membership-plans"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Plan deleted successfully");
    },
    onError: (err: any) => {
      toast.error("Failed to delete plan", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useCreateMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      member_id: string;
      plan_id: string;
      start_date?: string;
      create_payment?: boolean;
    }) => api.post<Membership>("/memberships", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memberships"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Membership assigned successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to create membership", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useRenewMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      membershipId,
      data,
    }: {
      membershipId: string;
      data: { plan_id?: string; start_date?: string; create_payment?: boolean };
    }) => api.post<Membership>(`/memberships/${membershipId}/renew`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memberships"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Membership renewed successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to renew membership", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useCancelMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (membershipId: string) =>
      api.patch<Membership>(`/memberships/${membershipId}`, {
        status: "cancelled",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memberships"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Membership cancelled");
    },
    onError: (err: any) => {
      toast.error("Failed to cancel membership", {
        description: err.detail || err.message,
      });
    },
  });
}
