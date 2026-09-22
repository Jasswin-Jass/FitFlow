"use client";

import React, { useState } from "react";
import {
  Search,
  Plus,
  User,
  Phone,
  Mail,
  Calendar,
  MoreVertical,
  Trash2,
  Edit2,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
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
  useMembers,
  useCreateMember,
  useUpdateMember,
  useDeleteMember,
} from "@/hooks/use-members";
import { formatDate } from "@/lib/utils";
import { Member } from "@/types/api";

export default function MembersPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useMembers({
    search,
    status: statusFilter,
    page,
    size: 15,
  });

  const createMember = useCreateMember();
  const updateMember = useUpdateMember();
  const deleteMember = useDeleteMember();

  // Add Member Dialog State
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    status: "active" as "active" | "inactive",
  });

  // Edit Member Dialog State
  const [editingMember, setEditingMember] = useState<Member | null>(null);

  // Delete Confirmation State
  const [deletingMember, setDeletingMember] = useState<Member | null>(null);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createMember.mutateAsync(formData);
    setIsAddOpen(false);
    setFormData({ name: "", email: "", phone: "", status: "active" });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingMember) return;
    await updateMember.mutateAsync({
      id: editingMember.id,
      data: {
        name: editingMember.name,
        email: editingMember.email,
        phone: editingMember.phone,
        status: editingMember.status,
      },
    });
    setEditingMember(null);
  };

  const handleDelete = async () => {
    if (!deletingMember) return;
    await deleteMember.mutateAsync(deletingMember.id);
    setDeletingMember(null);
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Member Directory"
        subtitle="Manage gym memberships, member profiles, and account statuses"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Controls Toolbar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1 max-w-md">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
              <Input
                placeholder="Search by name, email, or phone..."
                className="pl-9 h-9"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="h-9 rounded-md border border-zinc-800 bg-zinc-900 px-3 text-xs text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>

          <Button
            onClick={() => setIsAddOpen(true)}
            size="sm"
            className="gap-2 bg-indigo-600 hover:bg-indigo-700 h-9"
          >
            <Plus className="h-4 w-4" /> Add Member
          </Button>
        </div>

        {/* Member Table */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 overflow-hidden shadow-sm">
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800 bg-zinc-900/90">
                <TableHead>Member</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Join Date</TableHead>
                <TableHead>Current Plan</TableHead>
                <TableHead>Plan Expiry</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-zinc-500">
                    Loading member database...
                  </TableCell>
                </TableRow>
              ) : !data?.items || data.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-zinc-500">
                    No members found matching your search or filters.
                  </TableCell>
                </TableRow>
              ) : (
                data.items.map((member: Member) => (
                  <TableRow key={member.id} className="border-zinc-800/60">
                    <TableCell className="font-medium text-white">
                      <div className="flex items-center gap-2.5">
                        <div className="h-8 w-8 rounded-full bg-zinc-800 text-indigo-400 flex items-center justify-center text-xs font-semibold shrink-0">
                          {member.name.charAt(0)}
                        </div>
                        <div>
                          <span className="block font-medium text-zinc-100">{member.name}</span>
                          <span className="block text-[11px] text-zinc-400">
                            {member.gender || "—"} {member.age ? `• ${member.age} yrs` : ""}
                          </span>
                        </div>
                      </div>
                    </TableCell>

                    <TableCell>
                      <div className="text-xs space-y-0.5">
                        <div className="text-zinc-300">{member.email}</div>
                        <div className="text-zinc-500">{member.phone}</div>
                      </div>
                    </TableCell>

                    <TableCell>
                      <Badge
                        variant={member.status === "active" ? "success" : "secondary"}
                        className="capitalize"
                      >
                        {member.status}
                      </Badge>
                    </TableCell>

                    <TableCell className="text-xs text-zinc-400">
                      {formatDate(member.join_date)}
                    </TableCell>

                    <TableCell className="text-xs">
                      {member.membership_plan_name ? (
                        <span className="text-indigo-400 font-medium">
                          {member.membership_plan_name}
                        </span>
                      ) : (
                        <span className="text-zinc-500 italic">No active plan</span>
                      )}
                    </TableCell>

                    <TableCell className="text-xs">
                      {member.membership_end_date ? (
                        <span className="text-zinc-300">
                          {formatDate(member.membership_end_date)}
                        </span>
                      ) : (
                        <span className="text-zinc-500">—</span>
                      )}
                    </TableCell>

                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-zinc-400 hover:text-white"
                          onClick={() => setEditingMember(member)}
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-zinc-400 hover:text-red-400"
                          onClick={() => setDeletingMember(member)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* Pagination Toolbar */}
          {data && data.pages > 1 && (
            <div className="flex items-center justify-between px-6 py-3 border-t border-zinc-800 bg-zinc-950/40 text-xs text-zinc-400">
              <div>
                Showing {(page - 1) * data.size + 1} to{" "}
                {Math.min(page * data.size, data.total)} of {data.total} members
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                  className="h-7 w-7 p-0"
                >
                  <ChevronLeft className="h-3.5 w-3.5" />
                </Button>
                <span>
                  Page {page} of {data.pages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= data.pages}
                  onClick={() => setPage(page + 1)}
                  className="h-7 w-7 p-0"
                >
                  <ChevronRight className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* 1. Add Member Dialog */}
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogContent onClose={() => setIsAddOpen(false)}>
            <DialogHeader>
              <DialogTitle>Add New Gym Member</DialogTitle>
              <DialogDescription>
                Enter the member&apos;s personal and contact details.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Full Name</label>
                <Input
                  required
                  placeholder="e.g. Ramesh Kannan"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Email Address</label>
                <Input
                  type="email"
                  required
                  placeholder="ramesh.k@gmail.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Phone Number</label>
                <Input
                  required
                  placeholder="+91 98401 23456"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsAddOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={createMember.isPending}>
                  {createMember.isPending ? "Adding..." : "Save Member"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* 2. Edit Member Dialog */}
        <Dialog open={!!editingMember} onOpenChange={(open) => !open && setEditingMember(null)}>
          <DialogContent onClose={() => setEditingMember(null)}>
            <DialogHeader>
              <DialogTitle>Edit Member</DialogTitle>
              <DialogDescription>Update member contact info or account status.</DialogDescription>
            </DialogHeader>
            {editingMember && (
              <form onSubmit={handleUpdate} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Full Name</label>
                  <Input
                    required
                    value={editingMember.name}
                    onChange={(e) =>
                      setEditingMember({ ...editingMember, name: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Email</label>
                  <Input
                    type="email"
                    required
                    value={editingMember.email}
                    onChange={(e) =>
                      setEditingMember({ ...editingMember, email: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Phone</label>
                  <Input
                    required
                    value={editingMember.phone}
                    onChange={(e) =>
                      setEditingMember({ ...editingMember, phone: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Status</label>
                  <select
                    value={editingMember.status}
                    onChange={(e) =>
                      setEditingMember({
                        ...editingMember,
                        status: e.target.value as "active" | "inactive",
                      })
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
                    onClick={() => setEditingMember(null)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={updateMember.isPending}>
                    {updateMember.isPending ? "Saving..." : "Save Changes"}
                  </Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* 3. Delete Confirmation Dialog */}
        <Dialog open={!!deletingMember} onOpenChange={(open) => !open && setDeletingMember(null)}>
          <DialogContent onClose={() => setDeletingMember(null)}>
            <DialogHeader>
              <DialogTitle className="text-red-400">Delete Member</DialogTitle>
              <DialogDescription>
                Are you sure you want to permanently delete member{" "}
                <strong className="text-zinc-100">{deletingMember?.name}</strong>? All
                associated memberships and records will be deleted.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setDeletingMember(null)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={deleteMember.isPending}
              >
                {deleteMember.isPending ? "Deleting..." : "Delete Permanently"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
