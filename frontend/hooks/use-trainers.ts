"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { Trainer } from "@/types/api";

export function useTrainers() {
  return useQuery({
    queryKey: ["trainers"],
    queryFn: () => api.get<{ items: Trainer[]; total: number }>("/trainers"),
  });
}

export function useCreateTrainer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; email: string; specialty: string }) =>
      api.post<Trainer>("/trainers", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      toast.success("Trainer added successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to add trainer", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useUpdateTrainer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { name?: string; email?: string; specialty?: string };
    }) => api.patch<Trainer>(`/trainers/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      toast.success("Trainer updated successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to update trainer", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useDeleteTrainer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.delete(`/trainers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      toast.success("Trainer removed successfully");
    },
    onError: (err: any) => {
      toast.error("Failed to delete trainer", {
        description: err.detail || err.message,
      });
    },
  });
}
