"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import {
  Trainer,
  TrainerListResponse,
  TrainerClientListResponse,
  TrainerClientItem,
  TrainerReviewListResponse,
  TrainerReview,
} from "@/types/api";

export function useTrainers() {
  return useQuery({
    queryKey: ["trainers"],
    queryFn: () => api.get<TrainerListResponse>("/trainers"),
  });
}

export function useTrainer(id?: string | null) {
  return useQuery({
    queryKey: ["trainer", id],
    queryFn: () => api.get<Trainer>(`/trainers/${id}`),
    enabled: Boolean(id),
  });
}

export function useCreateTrainer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Trainer>) => api.post<Trainer>("/trainers", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
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
      data: Partial<Trainer>;
    }) => api.patch<Trainer>(`/trainers/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      queryClient.invalidateQueries({ queryKey: ["trainer", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
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
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Trainer removed successfully");
    },
    onError: (err: any) => {
      toast.error("Failed to delete trainer", {
        description: err.detail || err.message,
      });
    },
  });
}

// -------------------------------------------------------------
// Trainer Client Assignments Hooks
// -------------------------------------------------------------

export function useTrainerClients(trainerId?: string | null) {
  return useQuery({
    queryKey: ["trainer-clients", trainerId],
    queryFn: () =>
      api.get<TrainerClientListResponse>(`/trainers/${trainerId}/clients`),
    enabled: Boolean(trainerId),
  });
}

export function useAssignTrainerClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      trainerId,
      memberId,
    }: {
      trainerId: string;
      memberId: string;
    }) =>
      api.post<TrainerClientItem>(`/trainers/${trainerId}/clients`, {
        member_id: memberId,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      queryClient.invalidateQueries({ queryKey: ["trainer", variables.trainerId] });
      queryClient.invalidateQueries({
        queryKey: ["trainer-clients", variables.trainerId],
      });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Member assigned to trainer successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to assign client", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useUnassignTrainerClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      trainerId,
      memberId,
    }: {
      trainerId: string;
      memberId: string;
    }) => api.delete(`/trainers/${trainerId}/clients/${memberId}`),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      queryClient.invalidateQueries({ queryKey: ["trainer", variables.trainerId] });
      queryClient.invalidateQueries({
        queryKey: ["trainer-clients", variables.trainerId],
      });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Member unassigned successfully");
    },
    onError: (err: any) => {
      toast.error("Failed to unassign client", {
        description: err.detail || err.message,
      });
    },
  });
}

// -------------------------------------------------------------
// Trainer Reviews Hooks
// -------------------------------------------------------------

export function useTrainerReviews(trainerId?: string | null) {
  return useQuery({
    queryKey: ["trainer-reviews", trainerId],
    queryFn: () =>
      api.get<TrainerReviewListResponse>(`/trainers/${trainerId}/reviews`),
    enabled: Boolean(trainerId),
  });
}

export function useCreateTrainerReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      trainerId,
      data,
    }: {
      trainerId: string;
      data: { member_id: string; rating: number; review?: string };
    }) => api.post<TrainerReview>(`/trainers/${trainerId}/reviews`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["trainers"] });
      queryClient.invalidateQueries({ queryKey: ["trainer", variables.trainerId] });
      queryClient.invalidateQueries({
        queryKey: ["trainer-reviews", variables.trainerId],
      });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Review submitted successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to submit review", {
        description: err.detail || err.message,
      });
    },
  });
}
