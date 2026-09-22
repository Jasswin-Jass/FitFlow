"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { Member, MemberListResponse } from "@/types/api";

export function useMembers(params?: {
  search?: string;
  status?: string;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: ["members", params],
    queryFn: () =>
      api.get<MemberListResponse>("/members", {
        search: params?.search || undefined,
        status: params?.status === "all" ? undefined : params?.status,
        page: params?.page || 1,
        size: params?.size || 20,
      }),
  });
}

export function useMember(memberId?: string | null) {
  return useQuery({
    queryKey: ["member", memberId],
    queryFn: () => api.get<Member>(`/members/${memberId}`),
    enabled: Boolean(memberId),
  });
}

export function useCreateMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Member>) => api.post<Member>("/members", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Member added successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to create member", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useUpdateMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<Member>;
    }) => api.patch<Member>(`/members/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["member", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Member updated successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to update member", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useDeleteMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.delete(`/members/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Member deleted successfully");
    },
    onError: (err: any) => {
      toast.error("Failed to delete member", {
        description: err.detail || err.message,
      });
    },
  });
}
