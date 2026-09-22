"use client";

import React, { useState } from "react";
import {
  UserCheck,
  Plus,
  RefreshCw,
  XCircle,
  Clock,
  CheckCircle2,
  Calendar,
  AlertTriangle,
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
  useMemberships,
  useMembershipPlans,
  useCreateMembership,
  useRenewMembership,
  useCancelMembership,
} from "@/hooks/use-memberships";
import { useMembers } from "@/hooks/use-members";
import { formatDate, formatINR } from "@/lib/utils";
import { Membership, Member, MembershipPlan } from "@/types/api";

export default function MembershipsPage() {
  const [statusFilter, setStatusFilter] = useState("all");

  const { data: membershipsData, isLoading } = useMemberships(statusFilter);
  const { data: plansData, isLoading: isLoadingPlans } = useMembershipPlans();
  const { data: membersData } = useMembers({ size: 100 });

  const availablePlans: MembershipPlan[] = Array.isArray(plansData)
    ? plansData
    : Array.isArray((plansData as any)?.items)
    ? (plansData as any).items
    : [];

  const createMembership = useCreateMembership();
  const renewMembership = useRenewMembership();
  const cancelMembership = useCancelMembership();

  // Dialog States
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    member_id: "",
    plan_id: "",
    start_date: new Date().toISOString().split("T")[0],
    create_payment: true,
  });

  const [renewingItem, setRenewingItem] = useState<Membership | null>(null);
  const [renewPlanId, setRenewPlanId] = useState("");

  const [cancellingItem, setCancellingItem] = useState<Membership | null>(null);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createForm.member_id || !createForm.plan_id) return;
    await createMembership.mutateAsync(createForm);
    setIsCreateOpen(false);
    setCreateForm({
      member_id: "",
      plan_id: "",
      start_date: new Date().toISOString().split("T")[0],
      create_payment: true,
    });
  };

  const handleRenew = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!renewingItem) return;
    await renewMembership.mutateAsync({
      membershipId: renewingItem.id,
      data: {
        plan_id: renewPlanId || renewingItem.plan_id,
        create_payment: true,
      },
    });
    setRenewingItem(null);
  };

  const handleCancel = async () => {
    if (!cancellingItem) return;
    await cancelMembership.mutateAsync(cancellingItem.id);
    setCancellingItem(null);
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Memberships Management"
        subtitle="Track subscription plans, renewal cycles, and member contract statuses"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Actions bar */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            {["all", "active", "expired", "cancelled"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                  statusFilter === st
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {st === "all" ? "All Subscriptions" : st}
              </button>
            ))}
          </div>

          <Button
            onClick={() => setIsCreateOpen(true)}
            size="sm"
            className="gap-2 bg-indigo-600 hover:bg-indigo-700 h-9"
          >
            <Plus className="h-4 w-4" /> Assign New Membership
          </Button>
        </div>

        {/* Table */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 overflow-hidden shadow-sm">
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800 bg-zinc-900/90">
                <TableHead>Member</TableHead>
                <TableHead>Plan</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Start Date</TableHead>
                <TableHead>End Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-12 text-zinc-500">
                    Loading memberships...
                  </TableCell>
                </TableRow>
              ) : !membershipsData?.items || membershipsData.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-12 text-zinc-500">
                    No memberships found for the selected filter.
                  </TableCell>
                </TableRow>
              ) : (
                membershipsData.items.map((m: Membership) => {
                  const today = new Date();
                  today.setHours(0, 0, 0, 0);
                  const endDate = new Date(m.end_date);
                  const diffTime = endDate.getTime() - today.getTime();
                  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                  const isExpiringSoon = m.status === "active" && diffDays >= 0 && diffDays <= 7;

                  return (
                    <TableRow key={m.id} className="border-zinc-800/60">
                      <TableCell className="font-medium text-white">
                        <div>
                          <p>{m.member_name || "Unknown Member"}</p>
                          <p className="text-[11px] text-zinc-500">{m.member_email}</p>
                        </div>
                      </TableCell>

                      <TableCell className="text-indigo-300 font-medium text-xs">
                        {m.plan_name}
                      </TableCell>

                      <TableCell className="font-mono text-xs text-zinc-200">
                        {formatINR(m.plan_price)}
                      </TableCell>

                      <TableCell className="text-xs text-zinc-400">
                        {m.plan_duration_days} days
                      </TableCell>

                      <TableCell className="text-xs text-zinc-400">
                        {formatDate(m.start_date)}
                      </TableCell>

                      <TableCell className="text-xs font-medium">
                        <div className="flex items-center gap-1.5">
                          <span
                            className={
                              isExpiringSoon
                                ? "text-amber-400 font-semibold"
                                : m.status === "expired"
                                ? "text-red-400"
                                : "text-zinc-300"
                            }
                          >
                            {formatDate(m.end_date)}
                          </span>
                          {isExpiringSoon && (
                            <Badge variant="warning" className="text-[10px] py-0 px-1.5">
                              {diffDays}d left
                            </Badge>
                          )}
                        </div>
                      </TableCell>

                      <TableCell>
                        <Badge
                          variant={
                            m.status === "active"
                              ? isExpiringSoon
                                ? "warning"
                                : "success"
                              : m.status === "expired"
                              ? "destructive"
                              : "secondary"
                          }
                          className="capitalize"
                        >
                          {isExpiringSoon ? "Expiring Soon" : m.status}
                        </Badge>
                      </TableCell>

                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="secondary"
                            size="sm"
                            className="h-7 text-xs bg-zinc-800 hover:bg-zinc-700 gap-1"
                            onClick={() => {
                              setRenewingItem(m);
                              setRenewPlanId(m.plan_id);
                            }}
                          >
                            <RefreshCw className="h-3 w-3" /> Renew
                          </Button>
                          {m.status === "active" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 text-xs text-red-400 hover:text-red-300 hover:bg-red-950/30"
                              onClick={() => setCancellingItem(m)}
                            >
                              Cancel
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>

        {/* 1. Create Membership Dialog */}
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogContent onClose={() => setIsCreateOpen(false)}>
            <DialogHeader>
              <DialogTitle>Assign Membership</DialogTitle>
              <DialogDescription>
                Select the gym member and membership plan to activate.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Select Member</label>
                <select
                  required
                  value={createForm.member_id}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, member_id: e.target.value })
                  }
                  className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="">-- Choose Member --</option>
                  {membersData?.items.map((mem: Member) => (
                    <option key={mem.id} value={mem.id}>
                      {mem.name} ({mem.email})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Membership Plan</label>
                <select
                  required
                  value={createForm.plan_id}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, plan_id: e.target.value })
                  }
                  className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="">
                    {isLoadingPlans
                      ? "-- Loading plans... --"
                      : availablePlans.length === 0
                      ? "-- No plans available --"
                      : "-- Choose Plan --"}
                  </option>
                  {availablePlans.map((plan: MembershipPlan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name} — {formatINR(plan.price)} ({plan.duration_days} days)
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Start Date</label>
                <Input
                  type="date"
                  required
                  value={createForm.start_date}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, start_date: e.target.value })
                  }
                />
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="auto_pay"
                  checked={createForm.create_payment}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, create_payment: e.target.checked })
                  }
                  className="rounded border-zinc-700 bg-zinc-900 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="auto_pay" className="text-xs text-zinc-300">
                  Automatically record payment in full
                </label>
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsCreateOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={createMembership.isPending}>
                  {createMembership.isPending ? "Assigning..." : "Confirm Membership"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* 2. Renew Dialog */}
        <Dialog open={!!renewingItem} onOpenChange={(open) => !open && setRenewingItem(null)}>
          <DialogContent onClose={() => setRenewingItem(null)}>
            <DialogHeader>
              <DialogTitle>Renew Membership</DialogTitle>
              <DialogDescription>
                Renew membership for{" "}
                <strong className="text-zinc-100">{renewingItem?.member_name}</strong>.
              </DialogDescription>
            </DialogHeader>

            {renewingItem && (
              <form onSubmit={handleRenew} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Select Plan</label>
                  <select
                    value={renewPlanId}
                    onChange={(e) => setRenewPlanId(e.target.value)}
                    className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    {availablePlans.map((plan: MembershipPlan) => (
                      <option key={plan.id} value={plan.id}>
                        {plan.name} — {formatINR(plan.price)} ({plan.duration_days} days)
                      </option>
                    ))}
                  </select>
                </div>

                <div className="rounded-lg bg-zinc-800/40 p-3 text-xs text-zinc-400 space-y-1">
                  <p>
                    Current Expiry:{" "}
                    <span className="text-zinc-200 font-medium">
                      {formatDate(renewingItem.end_date)}
                    </span>
                  </p>
                  <p>Renewal will extend coverage and log a successful payment.</p>
                </div>

                <DialogFooter>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setRenewingItem(null)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={renewMembership.isPending}>
                    {renewMembership.isPending ? "Renewing..." : "Confirm Renewal"}
                  </Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* 3. Cancel Dialog */}
        <Dialog open={!!cancellingItem} onOpenChange={(open) => !open && setCancellingItem(null)}>
          <DialogContent onClose={() => setCancellingItem(null)}>
            <DialogHeader>
              <DialogTitle className="text-red-400">Cancel Membership</DialogTitle>
              <DialogDescription>
                Are you sure you want to cancel the active membership for{" "}
                <strong className="text-zinc-100">{cancellingItem?.member_name}</strong>?
                This will take them off active recurring revenue.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setCancellingItem(null)}
              >
                Keep Active
              </Button>
              <Button
                variant="destructive"
                onClick={handleCancel}
                disabled={cancelMembership.isPending}
              >
                {cancelMembership.isPending ? "Cancelling..." : "Yes, Cancel"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
