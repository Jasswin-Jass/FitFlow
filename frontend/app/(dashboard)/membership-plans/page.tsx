"use client";

import React, { useState } from "react";
import {
  Layers,
  Plus,
  Edit2,
  Trash2,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  useMembershipPlans,
  useCreatePlan,
  useUpdatePlan,
  useDeletePlan,
} from "@/hooks/use-memberships";
import { useAuth } from "@/hooks/use-auth";
import { formatINR } from "@/lib/utils";
import { MembershipPlan } from "@/types/api";

export default function MembershipPlansPage() {
  const { user } = useAuth();
  const { data: plansData, isLoading, isError, error } = useMembershipPlans();
  const createPlan = useCreatePlan();
  const updatePlan = useUpdatePlan();
  const deletePlan = useDeletePlan();

  const availablePlans = Array.isArray(plansData)
    ? plansData
    : plansData?.items || [];

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState<MembershipPlan | null>(null);
  const [deletingPlan, setDeletingPlan] = useState<MembershipPlan | null>(null);

  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    duration_days: "30",
    status: "active",
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createPlan.mutateAsync({
      name: form.name,
      description: form.description || undefined,
      price: parseFloat(form.price),
      duration_days: parseInt(form.duration_days, 10),
      status: form.status,
    });
    setIsAddOpen(false);
    setForm({ name: "", description: "", price: "", duration_days: "30", status: "active" });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPlan) return;
    await updatePlan.mutateAsync({
      id: editingPlan.id,
      data: {
        name: editingPlan.name,
        description: editingPlan.description,
        price: Number(editingPlan.price),
        duration_days: Number(editingPlan.duration_days),
        status: editingPlan.status,
      },
    });
    setEditingPlan(null);
  };

  const handleDelete = async () => {
    if (!deletingPlan) return;
    await deletePlan.mutateAsync(deletingPlan.id);
    setDeletingPlan(null);
  };

  const toggleStatus = async (plan: MembershipPlan) => {
    const nextStatus = plan.status === "inactive" ? "active" : "inactive";
    await updatePlan.mutateAsync({
      id: plan.id,
      data: { status: nextStatus },
    });
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Membership Plans"
        subtitle="Manage subscription tiers, pricing packages, duration cycles, and tier availability"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Top Action Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="text-xs text-zinc-400">
            {availablePlans.length} plans configured for{" "}
            <span className="text-zinc-200 font-semibold">{user?.gym_name}</span>
          </div>

          <Button
            onClick={() => setIsAddOpen(true)}
            size="sm"
            className="gap-2 bg-indigo-600 hover:bg-indigo-700 h-9"
          >
            <Plus className="h-4 w-4" /> Create Membership Plan
          </Button>
        </div>

        {/* Content Area */}
        {isLoading ? (
          <div className="py-24 text-center text-zinc-500 text-sm">
            Loading membership plans...
          </div>
        ) : isError ? (
          <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-8 text-center text-rose-300">
            Failed to load plans: {(error as any)?.message || "Internal API Error"}
          </div>
        ) : availablePlans.length === 0 ? (
          <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-900/30 p-12 text-center">
            <Layers className="mx-auto h-12 w-12 text-zinc-600 mb-3" />
            <h3 className="text-base font-semibold text-zinc-200">No membership plans yet</h3>
            <p className="text-xs text-zinc-400 mt-1 max-w-sm mx-auto">
              Create a plan to start assigning memberships and building gym recurring revenue.
            </p>
            <Button
              onClick={() => setIsAddOpen(true)}
              size="sm"
              className="mt-4 gap-2 bg-indigo-600 hover:bg-indigo-700 h-9"
            >
              <Plus className="h-4 w-4" /> Create Membership Plan
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availablePlans.map((plan: MembershipPlan) => {
              const isActive = (plan.status || "active") === "active";
              return (
                <Card
                  key={plan.id}
                  className={`border bg-zinc-900/50 transition-all hover:border-zinc-700 relative overflow-hidden ${
                    isActive ? "border-zinc-800/80" : "border-zinc-800/40 opacity-70"
                  }`}
                >
                  <div className="p-6 space-y-4">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-base font-bold text-white tracking-tight">
                          {plan.name}
                        </h3>
                        <p className="text-xs text-zinc-400 mt-1 line-clamp-2 min-h-[32px]">
                          {plan.description || "Full gym facility access and standard workout equipment."}
                        </p>
                      </div>
                      <Badge
                        variant="outline"
                        className={
                          isActive
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 text-[10px]"
                            : "bg-zinc-800 text-zinc-400 border-zinc-700 text-[10px]"
                        }
                      >
                        {isActive ? "Active" : "Inactive"}
                      </Badge>
                    </div>

                    <div className="pt-2 border-t border-zinc-800/60 flex items-baseline justify-between">
                      <div>
                        <span className="text-3xl font-bold font-mono text-white">
                          {formatINR(plan.price)}
                        </span>
                        <span className="text-xs text-zinc-400 ml-1.5">
                          / {plan.duration_days} days
                        </span>
                      </div>
                      <div className="text-[11px] text-zinc-500 flex items-center gap-1 font-mono">
                        <Clock className="h-3 w-3" />
                        <span>{Math.round(plan.duration_days / 30)} mo</span>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-zinc-800/60 flex items-center justify-between gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleStatus(plan)}
                        className={`text-xs h-8 px-2.5 ${
                          isActive
                            ? "text-zinc-400 hover:text-amber-400"
                            : "text-emerald-400 hover:text-emerald-300"
                        }`}
                      >
                        {isActive ? "Deactivate" : "Activate"}
                      </Button>

                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingPlan(plan)}
                          className="h-8 w-8 p-0 text-zinc-400 hover:text-white"
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeletingPlan(plan)}
                          className="h-8 w-8 p-0 text-zinc-400 hover:text-rose-400"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* 1. Create Plan Modal */}
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogContent onClose={() => setIsAddOpen(false)}>
            <DialogHeader>
              <DialogTitle>Create Membership Plan</DialogTitle>
              <DialogDescription>
                Define a new subscription pricing package for {user?.gym_name}.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Plan Name *</label>
                <Input
                  required
                  placeholder="e.g. Power Monthly, Summer Shred"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Price (₹) *</label>
                  <Input
                    required
                    type="number"
                    step="0.01"
                    min="1"
                    placeholder="1800"
                    value={form.price}
                    onChange={(e) => setForm({ ...form, price: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Duration (Days) *</label>
                  <select
                    value={form.duration_days}
                    onChange={(e) => setForm({ ...form, duration_days: e.target.value })}
                    className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="30">30 Days (1 Month)</option>
                    <option value="60">60 Days (2 Months)</option>
                    <option value="90">90 Days (Quarterly)</option>
                    <option value="180">180 Days (Half Year)</option>
                    <option value="365">365 Days (1 Year)</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Description</label>
                <Input
                  placeholder="Briefly describe what features and zones are included"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Status</label>
                <select
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                  className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="active">Active (Available for assignment)</option>
                  <option value="inactive">Inactive (Hidden from sales)</option>
                </select>
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsAddOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={createPlan.isPending}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  {createPlan.isPending ? "Creating..." : "Create Plan"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* 2. Edit Plan Modal */}
        <Dialog open={Boolean(editingPlan)} onOpenChange={(open) => !open && setEditingPlan(null)}>
          <DialogContent onClose={() => setEditingPlan(null)}>
            <DialogHeader>
              <DialogTitle>Edit Membership Plan</DialogTitle>
              <DialogDescription>
                Update pricing, duration, or tier details.
              </DialogDescription>
            </DialogHeader>

            {editingPlan && (
              <form onSubmit={handleUpdate} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Plan Name *</label>
                  <Input
                    required
                    value={editingPlan.name}
                    onChange={(e) =>
                      setEditingPlan({ ...editingPlan, name: e.target.value })
                    }
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Price (₹) *</label>
                    <Input
                      required
                      type="number"
                      step="0.01"
                      min="1"
                      value={editingPlan.price}
                      onChange={(e) =>
                        setEditingPlan({
                          ...editingPlan,
                          price: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Duration (Days) *</label>
                    <Input
                      required
                      type="number"
                      min="1"
                      value={editingPlan.duration_days}
                      onChange={(e) =>
                        setEditingPlan({
                          ...editingPlan,
                          duration_days: parseInt(e.target.value, 10) || 1,
                        })
                      }
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Description</label>
                  <Input
                    value={editingPlan.description || ""}
                    onChange={(e) =>
                      setEditingPlan({ ...editingPlan, description: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Status</label>
                  <select
                    value={editingPlan.status || "active"}
                    onChange={(e) =>
                      setEditingPlan({ ...editingPlan, status: e.target.value })
                    }
                    className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>

                <DialogFooter>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setEditingPlan(null)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={updatePlan.isPending}
                    className="bg-indigo-600 hover:bg-indigo-700"
                  >
                    {updatePlan.isPending ? "Saving..." : "Save Changes"}
                  </Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* 3. Delete Confirmation Dialog */}
        <Dialog open={Boolean(deletingPlan)} onOpenChange={(open) => !open && setDeletingPlan(null)}>
          <DialogContent onClose={() => setDeletingPlan(null)}>
            <DialogHeader>
              <DialogTitle>Delete Membership Plan</DialogTitle>
              <DialogDescription>
                Are you sure you want to remove &quot;{deletingPlan?.name}&quot;? Existing active memberships under this plan will remain valid.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setDeletingPlan(null)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={deletePlan.isPending}
              >
                {deletePlan.isPending ? "Deleting..." : "Delete Plan"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
