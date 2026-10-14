"use client";

import React, { useState } from "react";
import {
  CreditCard,
  Plus,
  Filter,
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle,
  RotateCcw,
  Zap,
  QrCode,
  ShieldCheck,
  ArrowRight,
  ExternalLink,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  usePayments,
  usePayment,
  useCreateSimulatedPayment,
  useSimulatePaymentSuccess,
  useSimulatePaymentFailure,
  useRetryPayment,
  useCancelPayment,
} from "@/hooks/use-payments";
import { useMembers } from "@/hooks/use-members";
import { useMemberships } from "@/hooks/use-memberships";
import { formatDate, formatINR } from "@/lib/utils";
import { Payment, Member, Membership } from "@/types/api";

export default function PaymentsPage() {
  const [statusFilter, setStatusFilter] = useState("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);

  // Queries
  const { data: paymentsData, isLoading } = usePayments({
    status: statusFilter,
    start_date: startDate,
    end_date: endDate,
    size: 50,
  });

  const { data: membersData } = useMembers({ size: 100 });
  const { data: membershipsData } = useMemberships();

  // Mutations
  const createPayment = useCreateSimulatedPayment();
  const simulateSuccess = useSimulatePaymentSuccess();
  const simulateFailure = useSimulatePaymentFailure();
  const retryPayment = useRetryPayment();
  const cancelPayment = useCancelPayment();

  // Dialog states
  const [isPayNowOpen, setIsPayNowOpen] = useState(false);
  const [createdPendingPayment, setCreatedPendingPayment] = useState<Payment | null>(null);

  // Form state
  const [memberId, setMemberId] = useState("");
  const [amount, setAmount] = useState<number>(1800);
  const [paymentMethod, setPaymentMethod] = useState<"upi" | "card" | "netbanking">("upi");
  const [selectedMembershipId, setSelectedMembershipId] = useState<string>("");

  // When member changes, find their active membership if any to auto-fill amount
  const handleMemberChange = (mId: string) => {
    setMemberId(mId);
    if (!mId) return;
    const activeShip = membershipsData?.items?.find(
      (ms: Membership) => ms.member_id === mId && ms.status === "active"
    );
    if (activeShip) {
      setSelectedMembershipId(activeShip.id);
      if (activeShip.plan_price) {
        setAmount(activeShip.plan_price);
      }
    } else {
      setSelectedMembershipId("");
    }
  };

  const handleCreatePaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!memberId) return;

    const res = await createPayment.mutateAsync({
      member_id: memberId,
      membership_id: selectedMembershipId || undefined,
      amount: Number(amount),
      currency: "INR",
      payment_method: paymentMethod,
    });

    setCreatedPendingPayment(res);
  };

  const handleSimulateSuccess = async (paymentId: string) => {
    await simulateSuccess.mutateAsync(paymentId);
    if (selectedPayment?.id === paymentId) {
      setSelectedPayment((prev) => (prev ? { ...prev, status: "paid" } : null));
    }
    if (createdPendingPayment?.id === paymentId) {
      setCreatedPendingPayment((prev) => (prev ? { ...prev, status: "paid" } : null));
    }
  };

  const handleSimulateFailure = async (paymentId: string, reason?: string) => {
    await simulateFailure.mutateAsync({
      paymentId,
      failure_reason: reason || "UPI PIN verification failed",
    });
    if (selectedPayment?.id === paymentId) {
      setSelectedPayment((prev) => (prev ? { ...prev, status: "failed", failure_reason: reason || "UPI PIN verification failed" } : null));
    }
    if (createdPendingPayment?.id === paymentId) {
      setCreatedPendingPayment((prev) => (prev ? { ...prev, status: "failed", failure_reason: reason || "UPI PIN verification failed" } : null));
    }
  };

  const handleRetry = async (paymentId: string) => {
    await retryPayment.mutateAsync(paymentId);
    if (selectedPayment?.id === paymentId) {
      setSelectedPayment((prev) => (prev ? { ...prev, status: "pending", failure_reason: null } : null));
    }
  };

  const handleCancel = async (paymentId: string) => {
    await cancelPayment.mutateAsync(paymentId);
    if (selectedPayment?.id === paymentId) {
      setSelectedPayment((prev) => (prev ? { ...prev, status: "cancelled" } : null));
    }
    if (createdPendingPayment?.id === paymentId) {
      setCreatedPendingPayment((prev) => (prev ? { ...prev, status: "cancelled" } : null));
    }
  };

  // Metric aggregates
  const items = paymentsData?.items || [];
  const totalPaidCount = items.filter((p) => p.status === "paid" || p.status === "success").length;
  const totalPaidAmount = items
    .filter((p) => p.status === "paid" || p.status === "success")
    .reduce((sum, p) => sum + p.amount, 0);
  const pendingCount = items.filter((p) => p.status === "pending").length;
  const failedCount = items.filter((p) => p.status === "failed").length;

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-zinc-950 text-zinc-100">
      <Header
        title="Payment Operations & Automation"
        subtitle="End-to-end automated billing, Pay Now checkout simulations, and multi-tenant ledger"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* KPI Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Total Collected</span>
              <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-2xl font-bold font-mono text-zinc-100">
              {formatINR(totalPaidAmount)}
            </div>
            <p className="mt-1 text-xs text-zinc-500">
              {totalPaidCount} successful transactions recorded
            </p>
          </div>

          <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Pending Payments</span>
              <div className="h-8 w-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
                <Clock className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-2xl font-bold font-mono text-amber-400">
              {pendingCount}
            </div>
            <p className="mt-1 text-xs text-zinc-500">Awaiting customer clearance or simulation</p>
          </div>

          <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Failed / Overdue</span>
              <div className="h-8 w-8 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400">
                <AlertCircle className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-2xl font-bold font-mono text-red-400">
              {failedCount}
            </div>
            <p className="mt-1 text-xs text-zinc-500">Requires retry or member outreach</p>
          </div>

          <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/20 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-indigo-300">Gateway Provider</span>
              <div className="h-8 w-8 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Zap className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-lg font-bold text-white flex items-center gap-2">
              <span>Demo Provider</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-normal">
                Active
              </span>
            </div>
            <p className="mt-1 text-xs text-indigo-300/70">Local Test Mode • No live KYC needed</p>
          </div>
        </div>

        {/* Filter Bar & Action Header */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          {/* Status Tabs */}
          <div className="flex items-center gap-1.5 p-1 bg-zinc-900/90 border border-zinc-800 rounded-lg overflow-x-auto">
            {[
              { id: "all", label: "All Payments" },
              { id: "paid", label: "Paid" },
              { id: "pending", label: "Pending" },
              { id: "failed", label: "Failed" },
              { id: "cancelled", label: "Cancelled" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap ${
                  statusFilter === tab.id
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Action Button: Pay Now / Create Payment */}
          <div className="flex items-center gap-3">
            <Button
              onClick={() => {
                setCreatedPendingPayment(null);
                setMemberId("");
                setAmount(1800);
                setIsPayNowOpen(true);
              }}
              size="sm"
              className="gap-2 bg-indigo-600 hover:bg-indigo-700 h-9 shrink-0 shadow-md shadow-indigo-600/20"
            >
              <Plus className="h-4 w-4" /> Pay Now / Create Payment
            </Button>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 overflow-hidden shadow-sm">
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800 bg-zinc-900/90">
                <TableHead>Member</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Mandate / Mode</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Interactive Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-zinc-500">
                    Loading payments...
                  </TableCell>
                </TableRow>
              ) : items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-zinc-500">
                    No payment transactions found matching criteria.
                  </TableCell>
                </TableRow>
              ) : (
                items.map((payment: Payment) => (
                  <TableRow
                    key={payment.id}
                    className="border-zinc-800/60 hover:bg-zinc-800/30 transition-colors"
                  >
                    {/* Member */}
                    <TableCell className="font-medium text-white">
                      <div>
                        <p className="font-semibold text-zinc-100">{payment.member_name || "Unknown Member"}</p>
                        <p className="text-[11px] text-zinc-500 font-mono">{payment.member_email}</p>
                      </div>
                    </TableCell>

                    {/* Amount */}
                    <TableCell className="font-mono font-semibold text-zinc-100">
                      {formatINR(payment.amount)}
                    </TableCell>

                    {/* Method */}
                    <TableCell>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium uppercase tracking-wider bg-zinc-800 text-zinc-300 border border-zinc-700/60">
                        {payment.payment_method || "upi"}
                      </span>
                    </TableCell>

                    {/* Auto Renewal / Mandate */}
                    <TableCell>
                      {payment.has_auto_renewal ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                          <Zap className="h-3 w-3" /> Auto-Renewal
                        </span>
                      ) : (
                        <span className="text-zinc-500 text-xs">One-Time</span>
                      )}
                    </TableCell>

                    {/* Date */}
                    <TableCell className="text-xs text-zinc-400">
                      {payment.paid_at ? (
                        formatDate(payment.paid_at)
                      ) : payment.due_date ? (
                        <span className="text-amber-400">Due {formatDate(payment.due_date)}</span>
                      ) : (
                        formatDate(payment.created_at || "")
                      )}
                    </TableCell>

                    {/* Status Badge */}
                    <TableCell>
                      <Badge
                        variant={
                          payment.status === "paid" || payment.status === "success"
                            ? "success"
                            : payment.status === "pending"
                            ? "warning"
                            : payment.status === "failed"
                            ? "destructive"
                            : "secondary"
                        }
                        className="capitalize"
                      >
                        {payment.status}
                      </Badge>
                    </TableCell>

                    {/* Actions */}
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {payment.status === "pending" && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleSimulateSuccess(payment.id)}
                              disabled={simulateSuccess.isPending}
                              className="h-7 text-xs border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 hover:text-emerald-300"
                            >
                              Simulate Paid
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleSimulateFailure(payment.id, "Bank timeout during UPI debit")}
                              disabled={simulateFailure.isPending}
                              className="h-7 text-xs border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
                            >
                              Simulate Fail
                            </Button>
                          </>
                        )}

                        {payment.status === "failed" && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRetry(payment.id)}
                            disabled={retryPayment.isPending}
                            className="h-7 text-xs border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
                          >
                            <RotateCcw className="h-3 w-3 mr-1" /> Retry
                          </Button>
                        )}

                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setSelectedPayment(payment)}
                          className="h-7 text-xs text-zinc-400 hover:text-zinc-100"
                        >
                          Details
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* PAY NOW / CREATE PAYMENT MODAL */}
        <Dialog open={isPayNowOpen} onOpenChange={setIsPayNowOpen}>
          <DialogContent onClose={() => setIsPayNowOpen(false)} className="max-w-xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-indigo-400" />
                <span>Simulated Payment Checkout</span>
              </DialogTitle>
              <DialogDescription>
                Initiate a payment transaction using FitFlow's decoupled Demo Gateway provider.
              </DialogDescription>
            </DialogHeader>

            {!createdPendingPayment ? (
              <form onSubmit={handleCreatePaymentSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Select Member</label>
                  <select
                    required
                    value={memberId}
                    onChange={(e) => handleMemberChange(e.target.value)}
                    className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="">-- Choose Member --</option>
                    {membersData?.items?.map((m: Member) => (
                      <option key={m.id} value={m.id}>
                        {m.name} ({m.email})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Amount (₹)</label>
                    <Input
                      type="number"
                      required
                      min={1}
                      value={amount}
                      onChange={(e) => setAmount(Number(e.target.value))}
                      className="bg-zinc-900 border-zinc-700"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Payment Method</label>
                    <select
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value as any)}
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="upi">UPI (Instant VPA / QR)</option>
                      <option value="card">Credit / Debit Card</option>
                      <option value="netbanking">Net Banking</option>
                    </select>
                  </div>
                </div>

                {/* Simulated Checkout Box */}
                <div className="rounded-xl border border-zinc-800 bg-zinc-900/80 p-4 space-y-3">
                  <div className="flex items-center justify-between text-xs text-zinc-400 border-b border-zinc-800 pb-2">
                    <span className="font-semibold text-zinc-200">Payment Breakdown</span>
                    <span className="px-2 py-0.5 rounded bg-zinc-800 text-[10px] text-zinc-400">Demo Provider</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-zinc-400">Subtotal</span>
                    <span className="font-mono text-zinc-200">{formatINR(amount)}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-zinc-400">Platform Convenience Fee</span>
                    <span className="font-mono text-emerald-400">₹0.00 (Waived)</span>
                  </div>
                  <div className="flex justify-between items-center text-base font-bold border-t border-zinc-800 pt-2">
                    <span className="text-white">Total Amount Due</span>
                    <span className="font-mono text-indigo-400">{formatINR(amount)}</span>
                  </div>
                </div>

                <DialogFooter className="pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsPayNowOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={createPayment.isPending || !memberId}
                    className="bg-indigo-600 hover:bg-indigo-700"
                  >
                    {createPayment.isPending ? "Creating Order..." : "Proceed to Simulated Checkout"}
                  </Button>
                </DialogFooter>
              </form>
            ) : (
              /* REALISTIC SIMULATED CHECKOUT SCREEN */
              <div className="space-y-5 py-2">
                <div className="p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/20 text-center space-y-2">
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold">
                    <Sparkles className="h-3.5 w-3.5" /> Demo Gateway Simulator
                  </div>
                  <h3 className="text-2xl font-bold font-mono text-white">
                    {formatINR(createdPendingPayment.amount)}
                  </h3>
                  <p className="text-xs text-zinc-400 font-mono">
                    Ref ID: {createdPendingPayment.provider_payment_id || createdPendingPayment.id}
                  </p>
                </div>

                {/* Simulated Payment Flow Interface */}
                {createdPendingPayment.status === "pending" ? (
                  <div className="space-y-4">
                    <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 space-y-3">
                      <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
                        {paymentMethod === "upi" ? (
                          <>
                            <QrCode className="h-4 w-4 text-emerald-400" />
                            <span>Simulated UPI Payment Request</span>
                          </>
                        ) : (
                          <>
                            <CreditCard className="h-4 w-4 text-indigo-400" />
                            <span>Simulated Card Authorization</span>
                          </>
                        )}
                      </div>
                      <p className="text-xs text-zinc-400">
                        In production, this initiates the Razorpay / UPI modal. In test mode, select an outcome below to test end-to-end automated state transitions.
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <Button
                        type="button"
                        onClick={() => handleSimulateSuccess(createdPendingPayment.id)}
                        disabled={simulateSuccess.isPending}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold"
                      >
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        Simulate Payment Success
                      </Button>

                      <Button
                        type="button"
                        variant="outline"
                        onClick={() =>
                          handleSimulateFailure(
                            createdPendingPayment.id,
                            "User cancelled UPI PIN authorization"
                          )
                        }
                        disabled={simulateFailure.isPending}
                        className="border-red-500/40 text-red-400 hover:bg-red-500/10"
                      >
                        <XCircle className="h-4 w-4 mr-2" />
                        Simulate Payment Failure
                      </Button>
                    </div>
                  </div>
                ) : createdPendingPayment.status === "paid" ? (
                  <div className="p-6 rounded-xl border border-emerald-500/30 bg-emerald-950/20 text-center space-y-3">
                    <div className="h-12 w-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                      <CheckCircle2 className="h-6 w-6" />
                    </div>
                    <h4 className="text-lg font-bold text-white">Payment Successful!</h4>
                    <p className="text-xs text-emerald-300">
                      Payment marked as paid. Member status active and subscription ledger updated.
                    </p>
                    <Button
                      onClick={() => setIsPayNowOpen(false)}
                      className="bg-emerald-600 hover:bg-emerald-700 mt-2"
                    >
                      Done
                    </Button>
                  </div>
                ) : (
                  <div className="p-6 rounded-xl border border-red-500/30 bg-red-950/20 text-center space-y-3">
                    <div className="h-12 w-12 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center mx-auto">
                      <XCircle className="h-6 w-6" />
                    </div>
                    <h4 className="text-lg font-bold text-white">Payment Failed</h4>
                    <p className="text-xs text-red-300">
                      {createdPendingPayment.failure_reason || "Transaction failed."}
                    </p>
                    <div className="flex items-center justify-center gap-3 pt-2">
                      <Button
                        variant="outline"
                        onClick={() => handleRetry(createdPendingPayment.id)}
                      >
                        Retry Payment
                      </Button>
                      <Button
                        variant="ghost"
                        onClick={() => setIsPayNowOpen(false)}
                      >
                        Close
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* PAYMENT DETAILS MODAL */}
        <Dialog open={!!selectedPayment} onOpenChange={(open) => !open && setSelectedPayment(null)}>
          <DialogContent onClose={() => setSelectedPayment(null)} className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center justify-between">
                <span>Payment Details</span>
                {selectedPayment && (
                  <Badge
                    variant={
                      selectedPayment.status === "paid" || selectedPayment.status === "success"
                        ? "success"
                        : selectedPayment.status === "pending"
                        ? "warning"
                        : selectedPayment.status === "failed"
                        ? "destructive"
                        : "secondary"
                    }
                    className="capitalize text-xs"
                  >
                    {selectedPayment.status}
                  </Badge>
                )}
              </DialogTitle>
              <DialogDescription>
                Provider reference and auditing trail.
              </DialogDescription>
            </DialogHeader>

            {selectedPayment && (
              <div className="space-y-4 text-xs">
                <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-4 space-y-3">
                  <div className="flex justify-between items-center py-1 border-b border-zinc-800">
                    <span className="text-zinc-400">Member</span>
                    <span className="font-semibold text-zinc-100">{selectedPayment.member_name}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-zinc-800">
                    <span className="text-zinc-400">Amount</span>
                    <span className="font-mono font-bold text-white text-sm">
                      {formatINR(selectedPayment.amount)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-zinc-800">
                    <span className="text-zinc-400">Payment Method</span>
                    <span className="uppercase font-mono text-zinc-300">
                      {selectedPayment.payment_method || "UPI"}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-zinc-800">
                    <span className="text-zinc-400">Provider</span>
                    <span className="text-indigo-400 font-mono">
                      {selectedPayment.provider || "demo"}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-zinc-800">
                    <span className="text-zinc-400">Provider Transaction ID</span>
                    <span className="font-mono text-zinc-300 text-[11px]">
                      {selectedPayment.provider_payment_id || selectedPayment.id}
                    </span>
                  </div>
                  {selectedPayment.paid_at && (
                    <div className="flex justify-between items-center py-1 border-b border-zinc-800">
                      <span className="text-zinc-400">Paid Timestamp</span>
                      <span className="text-zinc-300">{formatDate(selectedPayment.paid_at)}</span>
                    </div>
                  )}
                  {selectedPayment.failure_reason && (
                    <div className="flex justify-between items-center py-1 border-b border-zinc-800 text-red-400">
                      <span>Failure Reason</span>
                      <span className="font-medium text-right">{selectedPayment.failure_reason}</span>
                    </div>
                  )}
                </div>

                {/* State simulation triggers inside Details Modal */}
                <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/20 p-4 space-y-3">
                  <div className="flex items-center gap-1.5 text-indigo-300 font-semibold text-xs">
                    <Sparkles className="h-4 w-4" />
                    <span>Demo State Simulation Actions</span>
                  </div>
                  <p className="text-[11px] text-zinc-400">
                    Quickly test state machine behavior directly from this dialog.
                  </p>

                  <div className="flex flex-wrap gap-2 pt-1">
                    {selectedPayment.status === "pending" && (
                      <>
                        <Button
                          size="sm"
                          onClick={() => handleSimulateSuccess(selectedPayment.id)}
                          className="bg-emerald-600 hover:bg-emerald-700 text-xs"
                        >
                          Simulate Success
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleSimulateFailure(selectedPayment.id)}
                          className="border-red-500/40 text-red-400 hover:bg-red-500/10 text-xs"
                        >
                          Simulate Failure
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCancel(selectedPayment.id)}
                          className="text-zinc-400 text-xs"
                        >
                          Cancel Payment
                        </Button>
                      </>
                    )}

                    {selectedPayment.status === "failed" && (
                      <Button
                        size="sm"
                        onClick={() => handleRetry(selectedPayment.id)}
                        className="bg-amber-600 hover:bg-amber-700 text-xs text-white"
                      >
                        <RotateCcw className="h-3 w-3 mr-1" /> Re-open / Retry
                      </Button>
                    )}

                    {selectedPayment.status === "paid" && (
                      <div className="flex items-center gap-2 text-emerald-400 text-xs font-medium">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>Transaction finalized and verified.</span>
                      </div>
                    )}
                  </div>
                </div>

                <DialogFooter className="pt-2">
                  <Button variant="outline" onClick={() => setSelectedPayment(null)}>
                    Close
                  </Button>
                </DialogFooter>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
