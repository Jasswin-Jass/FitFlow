"use client";

import React, { useState } from "react";
import { CreditCard, Plus, Calendar, Filter, AlertCircle, CheckCircle2 } from "lucide-react";
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
import { usePayments, useCreatePayment } from "@/hooks/use-payments";
import { useMembers } from "@/hooks/use-members";
import { formatDate, formatINR } from "@/lib/utils";
import { Payment, Member } from "@/types/api";

export default function PaymentsPage() {
  const [statusFilter, setStatusFilter] = useState("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { data: paymentsData, isLoading } = usePayments({
    status: statusFilter,
    start_date: startDate,
    end_date: endDate,
    size: 25,
  });

  const { data: membersData } = useMembers({ size: 100 });
  const createPayment = useCreatePayment();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [form, setForm] = useState({
    member_id: "",
    amount: 1500,
    status: "success" as "success" | "failed" | "refunded",
  });

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.member_id) return;
    await createPayment.mutateAsync({
      member_id: form.member_id,
      amount: Number(form.amount),
      status: form.status,
    });
    setIsCreateOpen(false);
    setForm({ member_id: "", amount: 1500, status: "success" });
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Payment Transactions"
        subtitle="Audited financial transaction records, membership dues, and billing history"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Filter Controls */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-9 rounded-md border border-zinc-800 bg-zinc-900 px-3 text-xs text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="all">All Payment Statuses</option>
              <option value="success">Success Only</option>
              <option value="failed">Failed / Overdue Only</option>
              <option value="refunded">Refunded Only</option>
            </select>

            {/* Date Range */}
            <div className="flex items-center gap-1.5 text-xs text-zinc-400">
              <span>From:</span>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="h-9 w-36 text-xs"
              />
              <span>To:</span>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="h-9 w-36 text-xs"
              />
            </div>

            {(startDate || endDate || statusFilter !== "all") && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 text-xs text-zinc-400"
                onClick={() => {
                  setStatusFilter("all");
                  setStartDate("");
                  setEndDate("");
                }}
              >
                Clear Filters
              </Button>
            )}
          </div>

          <Button
            onClick={() => setIsCreateOpen(true)}
            size="sm"
            className="gap-2 bg-indigo-600 hover:bg-indigo-700 h-9 shrink-0"
          >
            <Plus className="h-4 w-4" /> Record Payment
          </Button>
        </div>

        {/* Transactions Table */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 overflow-hidden shadow-sm">
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800 bg-zinc-900/90">
                <TableHead>Member</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Associated Plan</TableHead>
                <TableHead>Date & Time</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-12 text-zinc-500">
                    Loading payments...
                  </TableCell>
                </TableRow>
              ) : !paymentsData?.items || paymentsData.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-12 text-zinc-500">
                    No payment transactions recorded yet.
                  </TableCell>
                </TableRow>
              ) : (
                paymentsData.items.map((payment: Payment) => (
                  <TableRow key={payment.id} className="border-zinc-800/60">
                    <TableCell className="font-medium text-white">
                      <div>
                        <p>{payment.member_name || "Unknown Member"}</p>
                        <p className="text-[11px] text-zinc-500">{payment.member_email}</p>
                      </div>
                    </TableCell>

                    <TableCell className="font-mono font-semibold text-zinc-100">
                      {formatINR(payment.amount)}
                    </TableCell>

                    <TableCell className="text-xs text-zinc-400">
                      {payment.plan_name ? (
                        <span className="text-indigo-400 font-medium">
                          {payment.plan_name}
                        </span>
                      ) : (
                        <span className="text-zinc-500 italic">Direct Payment</span>
                      )}
                    </TableCell>

                    <TableCell className="text-xs text-zinc-400">
                      {formatDate(payment.paid_at)}
                    </TableCell>

                    <TableCell>
                      <Badge
                        variant={
                          payment.status === "paid" || payment.status === "success"
                            ? "success"
                            : payment.status === "failed"
                            ? "destructive"
                            : "secondary"
                        }
                        className="capitalize"
                      >
                        {payment.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Record Payment Dialog */}
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogContent onClose={() => setIsCreateOpen(false)}>
            <DialogHeader>
              <DialogTitle>Record Payment Transaction</DialogTitle>
              <DialogDescription>
                Manually record a membership payment, renewal fee, or failed transaction.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleRecordPayment} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Member</label>
                <select
                  required
                  value={form.member_id}
                  onChange={(e) => setForm({ ...form, member_id: e.target.value })}
                  className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="">-- Choose Member --</option>
                  {membersData?.items.map((m: Member) => (
                    <option key={m.id} value={m.id}>
                      {m.name} ({m.email})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Amount (₹)</label>
                <Input
                  type="number"
                  required
                  min={1}
                  step="any"
                  value={form.amount}
                  onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Payment Status</label>
                <select
                  value={form.status}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      status: e.target.value as "success" | "failed" | "refunded",
                    })
                  }
                  className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="success">Success</option>
                  <option value="failed">Failed (Flags At-Risk Member)</option>
                  <option value="refunded">Refunded</option>
                </select>
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsCreateOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={createPayment.isPending}>
                  {createPayment.isPending ? "Recording..." : "Record Transaction"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
