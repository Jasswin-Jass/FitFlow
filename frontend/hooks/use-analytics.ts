"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import {
  AnalyticsOverviewResponse,
  MemberIntelligenceResponse,
  DemographicsResponse,
  RevenueIntelligenceResponse,
  MembershipIntelligenceResponse,
  TrainerIntelligenceResponse,
  ForecastResponse,
  InsightsResponse,
} from "@/types/api";

export function useAnalyticsOverview(targetDate?: string) {
  return useQuery({
    queryKey: ["analytics-overview", targetDate],
    queryFn: () =>
      api.get<AnalyticsOverviewResponse>("/analytics/overview", {
        target_date: targetDate,
      }),
    staleTime: 30 * 1000,
  });
}

export function useMemberIntelligence(targetDate?: string) {
  return useQuery({
    queryKey: ["analytics-members", targetDate],
    queryFn: () =>
      api.get<MemberIntelligenceResponse>("/analytics/members", {
        target_date: targetDate,
      }),
    staleTime: 30 * 1000,
  });
}

export function useDemographics() {
  return useQuery({
    queryKey: ["analytics-demographics"],
    queryFn: () =>
      api.get<DemographicsResponse>("/analytics/demographics"),
    staleTime: 60 * 1000,
  });
}

export function useRevenueIntelligence(targetDate?: string) {
  return useQuery({
    queryKey: ["analytics-revenue", targetDate],
    queryFn: () =>
      api.get<RevenueIntelligenceResponse>("/analytics/revenue", {
        target_date: targetDate,
      }),
    staleTime: 30 * 1000,
  });
}

export function useMembershipIntelligence(targetDate?: string) {
  return useQuery({
    queryKey: ["analytics-memberships", targetDate],
    queryFn: () =>
      api.get<MembershipIntelligenceResponse>("/analytics/memberships", {
        target_date: targetDate,
      }),
    staleTime: 30 * 1000,
  });
}

export function useTrainerIntelligence() {
  return useQuery({
    queryKey: ["analytics-trainers"],
    queryFn: () =>
      api.get<TrainerIntelligenceResponse>("/analytics/trainers"),
    staleTime: 30 * 1000,
  });
}

export function useForecast(targetDate?: string) {
  return useQuery({
    queryKey: ["analytics-forecast", targetDate],
    queryFn: () =>
      api.get<ForecastResponse>("/analytics/forecast", {
        target_date: targetDate,
      }),
    staleTime: 60 * 1000,
  });
}

export function useActionableInsights(targetDate?: string) {
  return useQuery({
    queryKey: ["analytics-insights", targetDate],
    queryFn: () =>
      api.get<InsightsResponse>("/analytics/insights", {
        target_date: targetDate,
      }),
    staleTime: 30 * 1000,
  });
}
