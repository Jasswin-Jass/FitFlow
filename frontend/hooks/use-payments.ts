"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import {
  Payment,
  PaymentListResponse,
  PaymentSubscription,
  PaymentReminder,
  AutomationStatusResponse,
  DuePaymentsProcessResponse,
  CreatePaymentPayload,
  EnableAutoRenewalPayload,
} from "@/types/api";

// ----------------------------------------------------
// 1. Pay Now & Payment Lifecycle Hooks
// ----------------------------------------------------

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

export function usePayment(paymentId: string | null) {
  return useQuery({
    queryKey: ["payment", paymentId],
    queryFn: () => api.get<Payment>(`/payments/${paymentId}`),
    enabled: !!paymentId,
  });
}

export function useCreateSimulatedPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreatePaymentPayload) =>
      api.post<Payment>("/payments/create", payload),
    onSuccess: (payment) => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      toast.success("Payment transaction initiated!", {
        description: `Reference: ${payment.provider_payment_id || payment.id}`,
      });
    },
    onError: (err: any) => {
      toast.error("Failed to initiate payment", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useSimulatePaymentSuccess() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paymentId: string) =>
      api.post<Payment>(`/payments/${paymentId}/simulate-success`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["payment"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.success("Payment simulation: SUCCESS!", {
        description: "Transaction marked as paid and membership verified.",
      });
    },
    onError: (err: any) => {
      toast.error("Simulation failed", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useSimulatePaymentFailure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      paymentId,
      failure_reason,
    }: {
      paymentId: string;
      failure_reason?: string;
    }) =>
      api.post<Payment>(`/payments/${paymentId}/simulate-failure`, {
        failure_reason,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["payment"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      toast.error("Payment simulation: FAILED", {
        description: "Payment failed and member flagged for follow-up.",
      });
    },
    onError: (err: any) => {
      toast.error("Simulation failed", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useRetryPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paymentId: string) =>
      api.post<Payment>(`/payments/${paymentId}/retry`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["payment"] });
      toast.success("Payment re-opened for retry!");
    },
    onError: (err: any) => {
      toast.error("Retry failed", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useCancelPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paymentId: string) =>
      api.post<Payment>(`/payments/${paymentId}/cancel`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["payment"] });
      toast.info("Payment cancelled.");
    },
    onError: (err: any) => {
      toast.error("Cancellation failed", {
        description: err.detail || err.message,
      });
    },
  });
}

// ----------------------------------------------------
// 2. Auto-Renewal / Recurring Mandates Hooks
// ----------------------------------------------------

export function useMemberSubscription(memberId: string | null) {
  return useQuery({
    queryKey: ["member-subscription", memberId],
    queryFn: () =>
      api.get<PaymentSubscription | null>(
        `/payments/member/${memberId}/subscription`
      ),
    enabled: !!memberId,
  });
}

export function useEnableAutoRenewal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: EnableAutoRenewalPayload) =>
      api.post<PaymentSubscription>("/payments/auto-renewal", payload),
    onSuccess: (sub) => {
      queryClient.invalidateQueries({ queryKey: ["member-subscription"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["automation-status"] });
      toast.success("Auto-renewal mandate activated!", {
        description: `Billed ${sub.billing_interval}. Next billing: ${sub.next_billing_date}`,
      });
    },
    onError: (err: any) => {
      toast.error("Failed to enable auto-renewal", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useCancelAutoRenewal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (subscriptionId: string) =>
      api.delete<PaymentSubscription>(
        `/payments/auto-renewal/${subscriptionId}`
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["member-subscription"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["automation-status"] });
      toast.info("Auto-renewal mandate cancelled.");
    },
    onError: (err: any) => {
      toast.error("Failed to cancel auto-renewal", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useSimulateRecurringSuccess() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (subscriptionId: string) =>
      api.post<any>(`/payments/auto-renewal/${subscriptionId}/simulate-charge`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["member-subscription"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["automation-status"] });
      toast.success("Recurring auto-debit executed successfully!", {
        description: "Membership extended and invoice receipt generated.",
      });
    },
    onError: (err: any) => {
      toast.error("Auto-debit simulation failed", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useSimulateRecurringFailure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (subscriptionId: string) =>
      api.post<any>(`/payments/auto-renewal/${subscriptionId}/simulate-failure`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["member-subscription"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["automation-status"] });
      toast.error("Recurring auto-debit failed!", {
        description: "Subscription marked as past due and failure notification sent.",
      });
    },
    onError: (err: any) => {
      toast.error("Simulation failed", {
        description: err.detail || err.message,
      });
    },
  });
}

// ----------------------------------------------------
// 3. Automation, Batch Runner & Reminders Hooks
// ----------------------------------------------------

export function useProcessDuePayments() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      api.post<DuePaymentsProcessResponse>("/admin/process-due-payments"),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["automation-status"] });
      queryClient.invalidateQueries({ queryKey: ["payment-reminders"] });
      toast.success(`Batch runner completed!`, {
        description: `Processed: ${res.processed}, Succeeded: ${res.succeeded}, Collected: ₹${res.total_collected.toLocaleString("en-IN")}`,
      });
    },
    onError: (err: any) => {
      toast.error("Batch payment runner failed", {
        description: err.detail || err.message,
      });
    },
  });
}

export function useAutomationStatus() {
  return useQuery({
    queryKey: ["automation-status"],
    queryFn: () => api.get<AutomationStatusResponse>("/automation/status"),
  });
}

export function usePaymentReminders() {
  return useQuery({
    queryKey: ["payment-reminders"],
    queryFn: () => api.get<PaymentReminder[]>("/automation/reminders"),
  });
}

export function useTriggerChecks() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => api.post<{ status: string; triggered_at: string }>("/automation/trigger-checks"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payment-reminders"] });
      queryClient.invalidateQueries({ queryKey: ["automation-status"] });
      toast.success("Automated reminder check triggered successfully!");
    },
    onError: (err: any) => {
      toast.error("Failed to trigger automated checks", {
        description: err.detail || err.message,
      });
    },
  });
}

