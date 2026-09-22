"use client";

import React, { useState } from "react";
import {
  Search,
  Plus,
  User,
  Phone,
  Mail,
  Calendar,
  Trash2,
  Edit2,
  Eye,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  TrendingUp,
  Dumbbell,
  CheckCircle2,
  Clock,
  MapPin,
  Briefcase,
  Target,
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
  useMembers,
  useCreateMember,
  useUpdateMember,
  useDeleteMember,
} from "@/hooks/use-members";
import { useTrainers } from "@/hooks/use-trainers";
import { formatDate, formatINR } from "@/lib/utils";
import { Member } from "@/types/api";

function computeAge(dobStr?: string | null): number | null {
  if (!dobStr) return null;
  const birth = new Date(dobStr);
  if (isNaN(birth.getTime())) return null;
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age >= 0 ? age : null;
}

const initialFormState = {
  name: "",
  email: "",
  phone: "",
  date_of_birth: "",
  gender: "",
  city: "",
  occupation: "",
  fitness_goal: "",
  preferred_training_time: "",
  trainer_id: "",
  join_date: new Date().toISOString().split("T")[0],
  acquisition_source: "",
  referral_source: "",
  status: "active" as "active" | "inactive",
};

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

  const { data: trainersData } = useTrainers();
  const trainersList = trainersData?.items || [];

  const createMember = useCreateMember();
  const updateMember = useUpdateMember();
  const deleteMember = useDeleteMember();

  // Add Member State
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [addForm, setAddForm] = useState(initialFormState);

  // Edit Member State
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [editForm, setEditForm] = useState(initialFormState);

  // Detail Modal State
  const [detailMember, setDetailMember] = useState<Member | null>(null);

  // Delete Confirmation State
  const [deletingMember, setDeletingMember] = useState<Member | null>(null);

  const sanitizePayload = (form: typeof initialFormState) => ({
    name: form.name.trim(),
    email: form.email.trim(),
    phone: form.phone.trim(),
    date_of_birth: form.date_of_birth || null,
    gender: form.gender || null,
    city: form.city.trim() || null,
    occupation: form.occupation.trim() || null,
    fitness_goal: form.fitness_goal || null,
    preferred_training_time: form.preferred_training_time || null,
    trainer_id: form.trainer_id || null,
    join_date: form.join_date || undefined,
    acquisition_source: form.acquisition_source || null,
    referral_source: form.referral_source.trim() || null,
    status: form.status,
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createMember.mutateAsync(sanitizePayload(addForm));
    setIsAddOpen(false);
    setAddForm(initialFormState);
  };

  const openEditModal = (m: Member) => {
    setEditingMember(m);
    setEditForm({
      name: m.name || "",
      email: m.email || "",
      phone: m.phone || "",
      date_of_birth: m.date_of_birth ? m.date_of_birth.substring(0, 10) : "",
      gender: m.gender || "",
      city: m.city || "",
      occupation: m.occupation || "",
      fitness_goal: m.fitness_goal || "",
      preferred_training_time: m.preferred_training_time || "",
      trainer_id: m.trainer_id || "",
      join_date: m.join_date ? m.join_date.substring(0, 10) : "",
      acquisition_source: m.acquisition_source || "",
      referral_source: m.referral_source || "",
      status: (m.status as "active" | "inactive") || "active",
    });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingMember) return;
    await updateMember.mutateAsync({
      id: editingMember.id,
      data: sanitizePayload(editForm),
    });
    setEditingMember(null);
  };

  const handleDelete = async () => {
    if (!deletingMember) return;
    await deleteMember.mutateAsync(deletingMember.id);
    setDeletingMember(null);
    if (detailMember?.id === deletingMember.id) {
      setDetailMember(null);
    }
  };

  const maxDobDate = new Date().toISOString().split("T")[0];

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Member Directory"
        subtitle="Manage gym memberships, rich demographics, fitness profiles, and account health"
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
            onClick={() => {
              setAddForm(initialFormState);
              setIsAddOpen(true);
            }}
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
                <TableHead>Contact & City</TableHead>
                <TableHead>Demographics</TableHead>
                <TableHead>Status & Health</TableHead>
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
                data.items.map((member: Member) => {
                  const displayAge = member.age ?? computeAge(member.date_of_birth);
                  return (
                    <TableRow
                      key={member.id}
                      className="border-zinc-800/60 hover:bg-zinc-800/20 cursor-pointer"
                      onClick={() => setDetailMember(member)}
                    >
                      <TableCell className="font-medium text-white">
                        <div className="flex items-center gap-2.5">
                          <div className="h-8 w-8 rounded-full bg-zinc-800 text-indigo-400 flex items-center justify-center text-xs font-semibold shrink-0">
                            {member.name.charAt(0)}
                          </div>
                          <div>
                            <span className="block font-medium text-zinc-100">{member.name}</span>
                            <span className="block text-[11px] text-zinc-400">
                              Joined {formatDate(member.join_date)}
                            </span>
                          </div>
                        </div>
                      </TableCell>

                      <TableCell onClick={(e) => e.stopPropagation()}>
                        <div className="text-xs space-y-0.5">
                          <div className="text-zinc-300">{member.email}</div>
                          <div className="text-zinc-500 flex items-center gap-1.5">
                            <span>{member.phone}</span>
                            {member.city && (
                              <span className="text-zinc-600">• {member.city}</span>
                            )}
                          </div>
                        </div>
                      </TableCell>

                      <TableCell>
                        <div className="text-xs space-y-0.5">
                          <div className="text-zinc-200 font-medium">
                            {member.gender || "Not specified"}
                          </div>
                          <div className="text-zinc-400 text-[11px]">
                            {displayAge != null ? `${displayAge} yrs old` : "DOB not set"}
                          </div>
                        </div>
                      </TableCell>

                      <TableCell>
                        <div className="flex flex-col gap-1 items-start">
                          <Badge
                            variant={member.status === "active" ? "success" : "secondary"}
                            className="capitalize text-[11px]"
                          >
                            {member.status}
                          </Badge>
                          {member.is_at_risk && (
                            <Badge
                              variant="destructive"
                              className="text-[10px] px-1.5 py-0 bg-red-950/80 text-red-400 border border-red-800/50"
                            >
                              At Risk
                            </Badge>
                          )}
                        </div>
                      </TableCell>

                      <TableCell className="text-xs">
                        {member.membership_plan_name ? (
                          <div>
                            <span className="text-indigo-400 font-medium block">
                              {member.membership_plan_name}
                            </span>
                            {member.trainer_name && (
                              <span className="text-[11px] text-zinc-500 flex items-center gap-1">
                                <Dumbbell className="h-2.5 w-2.5" />
                                {member.trainer_name}
                              </span>
                            )}
                          </div>
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

                      <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-zinc-400 hover:text-indigo-400"
                            title="View Profile Details"
                            onClick={() => setDetailMember(member)}
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-zinc-400 hover:text-white"
                            title="Edit Member"
                            onClick={() => openEditModal(member)}
                          >
                            <Edit2 className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-zinc-400 hover:text-red-400"
                            title="Delete Member"
                            onClick={() => setDeletingMember(member)}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
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

        {/* ========================================================= */}
        {/* 1. Add Member Dialog (Sectioned Form) */}
        {/* ========================================================= */}
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen} className="max-w-2xl">
          <DialogContent onClose={() => setIsAddOpen(false)} className="max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-lg font-bold text-white flex items-center gap-2">
                <User className="h-5 w-5 text-indigo-400" />
                Add New Gym Member
              </DialogTitle>
              <DialogDescription>
                Collect complete personal demographics, fitness goals, and onboarding info.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleCreate} className="space-y-6 pt-2">
              {/* Section 1: Personal Demographics */}
              <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                  <User className="h-4 w-4" /> Personal Demographics
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div className="space-y-1.5 sm:col-span-2">
                    <label className="text-xs font-medium text-zinc-300">
                      Full Name <span className="text-red-400">*</span>
                    </label>
                    <Input
                      required
                      placeholder="e.g. Ramesh Kannan"
                      value={addForm.name}
                      onChange={(e) => setAddForm({ ...addForm, name: e.target.value })}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">
                      Email Address <span className="text-red-400">*</span>
                    </label>
                    <Input
                      type="email"
                      required
                      placeholder="ramesh.k@gmail.com"
                      value={addForm.email}
                      onChange={(e) => setAddForm({ ...addForm, email: e.target.value })}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">
                      Phone Number <span className="text-red-400">*</span>
                    </label>
                    <Input
                      required
                      placeholder="+91 98401 23456"
                      value={addForm.phone}
                      onChange={(e) => setAddForm({ ...addForm, phone: e.target.value })}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-medium text-zinc-300">Date of Birth</label>
                      {addForm.date_of_birth && (
                        <span className="text-[11px] font-mono text-indigo-400">
                          {computeAge(addForm.date_of_birth) != null
                            ? `Age: ${computeAge(addForm.date_of_birth)} yrs`
                            : ""}
                        </span>
                      )}
                    </div>
                    <Input
                      type="date"
                      max={maxDobDate}
                      value={addForm.date_of_birth}
                      onChange={(e) => setAddForm({ ...addForm, date_of_birth: e.target.value })}
                    />
                    <p className="text-[10px] text-zinc-500">Age is automatically calculated from DOB.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Gender</label>
                    <select
                      value={addForm.gender}
                      onChange={(e) => setAddForm({ ...addForm, gender: e.target.value })}
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="">-- Select Gender --</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                      <option value="Prefer not to say">Prefer not to say</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Section 2: Location & Profession */}
              <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                  <MapPin className="h-4 w-4" /> Location & Profession
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">City</label>
                    <Input
                      placeholder="e.g. Chennai, Bangalore"
                      value={addForm.city}
                      onChange={(e) => setAddForm({ ...addForm, city: e.target.value })}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Occupation</label>
                    <Input
                      placeholder="e.g. Software Engineer, Doctor"
                      value={addForm.occupation}
                      onChange={(e) => setAddForm({ ...addForm, occupation: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              {/* Section 3: Fitness Profile */}
              <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                  <Target className="h-4 w-4" /> Fitness Profile & Goals
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Primary Fitness Goal</label>
                    <select
                      value={addForm.fitness_goal}
                      onChange={(e) => setAddForm({ ...addForm, fitness_goal: e.target.value })}
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="">-- Select Goal --</option>
                      <option value="Weight Loss">Weight Loss</option>
                      <option value="Muscle Gain">Muscle Gain</option>
                      <option value="Endurance">Endurance</option>
                      <option value="General Fitness">General Fitness</option>
                      <option value="Rehab">Rehab & Mobility</option>
                      <option value="Athletic">Athletic Conditioning</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Preferred Training Time</label>
                    <select
                      value={addForm.preferred_training_time}
                      onChange={(e) =>
                        setAddForm({ ...addForm, preferred_training_time: e.target.value })
                      }
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="">-- Select Training Window --</option>
                      <option value="Morning">Morning (6 AM - 10 AM)</option>
                      <option value="Afternoon">Afternoon (12 PM - 4 PM)</option>
                      <option value="Evening">Evening (5 PM - 9 PM)</option>
                      <option value="Night">Night (9 PM - 11 PM)</option>
                    </select>
                  </div>

                  <div className="space-y-1.5 sm:col-span-2">
                    <label className="text-xs font-medium text-zinc-300">Assigned Coach / Trainer</label>
                    <select
                      value={addForm.trainer_id}
                      onChange={(e) => setAddForm({ ...addForm, trainer_id: e.target.value })}
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="">-- None / Unassigned --</option>
                      {trainersList.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.name} ({t.specialization || t.specialty || "Fitness"})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Section 4: Business & Onboarding */}
              <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                  <Briefcase className="h-4 w-4" /> Business & Acquisition
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Join Date</label>
                    <Input
                      type="date"
                      value={addForm.join_date}
                      onChange={(e) => setAddForm({ ...addForm, join_date: e.target.value })}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Acquisition Source</label>
                    <select
                      value={addForm.acquisition_source}
                      onChange={(e) =>
                        setAddForm({ ...addForm, acquisition_source: e.target.value })
                      }
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="">-- Select Source --</option>
                      <option value="Walk-in">Walk-in</option>
                      <option value="Referral">Member Referral</option>
                      <option value="Social Media">Social Media (Instagram/FB)</option>
                      <option value="Google Ads">Google Ads / Maps</option>
                      <option value="Event">Community Event</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Referral Details</label>
                    <Input
                      placeholder="e.g. Referred by Priya S."
                      value={addForm.referral_source}
                      onChange={(e) =>
                        setAddForm({ ...addForm, referral_source: e.target.value })
                      }
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Account Status</label>
                    <select
                      value={addForm.status}
                      onChange={(e) =>
                        setAddForm({
                          ...addForm,
                          status: e.target.value as "active" | "inactive",
                        })
                      }
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </div>
              </div>

              <DialogFooter className="pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsAddOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={createMember.isPending}>
                  {createMember.isPending ? "Adding Member..." : "Save Member"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* 2. Edit Member Dialog (Sectioned Form) */}
        {/* ========================================================= */}
        <Dialog
          open={!!editingMember}
          onOpenChange={(open) => !open && setEditingMember(null)}
          className="max-w-2xl"
        >
          <DialogContent onClose={() => setEditingMember(null)} className="max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-lg font-bold text-white flex items-center gap-2">
                <Edit2 className="h-5 w-5 text-indigo-400" />
                Edit Member Details
              </DialogTitle>
              <DialogDescription>
                Update demographics, fitness goals, trainer assignment, or account status.
              </DialogDescription>
            </DialogHeader>

            {editingMember && (
              <form onSubmit={handleUpdate} className="space-y-6 pt-2">
                {/* Section 1: Personal Demographics */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                    <User className="h-4 w-4" /> Personal Demographics
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                    <div className="space-y-1.5 sm:col-span-2">
                      <label className="text-xs font-medium text-zinc-300">
                        Full Name <span className="text-red-400">*</span>
                      </label>
                      <Input
                        required
                        value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">
                        Email Address <span className="text-red-400">*</span>
                      </label>
                      <Input
                        type="email"
                        required
                        value={editForm.email}
                        onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">
                        Phone Number <span className="text-red-400">*</span>
                      </label>
                      <Input
                        required
                        value={editForm.phone}
                        onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                      />
                    </div>

                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <label className="text-xs font-medium text-zinc-300">Date of Birth</label>
                        {editForm.date_of_birth && (
                          <span className="text-[11px] font-mono text-indigo-400">
                            {computeAge(editForm.date_of_birth) != null
                              ? `Age: ${computeAge(editForm.date_of_birth)} yrs`
                              : ""}
                          </span>
                        )}
                      </div>
                      <Input
                        type="date"
                        max={maxDobDate}
                        value={editForm.date_of_birth}
                        onChange={(e) =>
                          setEditForm({ ...editForm, date_of_birth: e.target.value })
                        }
                      />
                      <p className="text-[10px] text-zinc-500">Age is automatically calculated from DOB.</p>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Gender</label>
                      <select
                        value={editForm.gender}
                        onChange={(e) => setEditForm({ ...editForm, gender: e.target.value })}
                        className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="">-- Select Gender --</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                        <option value="Prefer not to say">Prefer not to say</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Section 2: Location & Profession */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                    <MapPin className="h-4 w-4" /> Location & Profession
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">City</label>
                      <Input
                        placeholder="e.g. Chennai, Bangalore"
                        value={editForm.city}
                        onChange={(e) => setEditForm({ ...editForm, city: e.target.value })}
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Occupation</label>
                      <Input
                        placeholder="e.g. Software Engineer, Doctor"
                        value={editForm.occupation}
                        onChange={(e) =>
                          setEditForm({ ...editForm, occupation: e.target.value })
                        }
                      />
                    </div>
                  </div>
                </div>

                {/* Section 3: Fitness Profile */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                    <Target className="h-4 w-4" /> Fitness Profile & Goals
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Primary Fitness Goal</label>
                      <select
                        value={editForm.fitness_goal}
                        onChange={(e) =>
                          setEditForm({ ...editForm, fitness_goal: e.target.value })
                        }
                        className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="">-- Select Goal --</option>
                        <option value="Weight Loss">Weight Loss</option>
                        <option value="Muscle Gain">Muscle Gain</option>
                        <option value="Endurance">Endurance</option>
                        <option value="General Fitness">General Fitness</option>
                        <option value="Rehab">Rehab & Mobility</option>
                        <option value="Athletic">Athletic Conditioning</option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Preferred Training Time</label>
                      <select
                        value={editForm.preferred_training_time}
                        onChange={(e) =>
                          setEditForm({ ...editForm, preferred_training_time: e.target.value })
                        }
                        className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="">-- Select Training Window --</option>
                        <option value="Morning">Morning (6 AM - 10 AM)</option>
                        <option value="Afternoon">Afternoon (12 PM - 4 PM)</option>
                        <option value="Evening">Evening (5 PM - 9 PM)</option>
                        <option value="Night">Night (9 PM - 11 PM)</option>
                      </select>
                    </div>

                    <div className="space-y-1.5 sm:col-span-2">
                      <label className="text-xs font-medium text-zinc-300">Assigned Coach / Trainer</label>
                      <select
                        value={editForm.trainer_id}
                        onChange={(e) => setEditForm({ ...editForm, trainer_id: e.target.value })}
                        className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="">-- None / Unassigned --</option>
                        {trainersList.map((t) => (
                          <option key={t.id} value={t.id}>
                            {t.name} ({t.specialization || t.specialty || "Fitness"})
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                {/* Section 4: Business & Onboarding */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 space-y-4">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                    <Briefcase className="h-4 w-4" /> Business & Acquisition
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Join Date</label>
                      <Input
                        type="date"
                        value={editForm.join_date}
                        onChange={(e) => setEditForm({ ...editForm, join_date: e.target.value })}
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Acquisition Source</label>
                      <select
                        value={editForm.acquisition_source}
                        onChange={(e) =>
                          setEditForm({ ...editForm, acquisition_source: e.target.value })
                        }
                        className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="">-- Select Source --</option>
                        <option value="Walk-in">Walk-in</option>
                        <option value="Referral">Member Referral</option>
                        <option value="Social Media">Social Media (Instagram/FB)</option>
                        <option value="Google Ads">Google Ads / Maps</option>
                        <option value="Event">Community Event</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Referral Details</label>
                      <Input
                        placeholder="e.g. Referred by Priya S."
                        value={editForm.referral_source}
                        onChange={(e) =>
                          setEditForm({ ...editForm, referral_source: e.target.value })
                        }
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-zinc-300">Account Status</label>
                      <select
                        value={editForm.status}
                        onChange={(e) =>
                          setEditForm({
                            ...editForm,
                            status: e.target.value as "active" | "inactive",
                          })
                        }
                        className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </div>
                  </div>
                </div>

                <DialogFooter className="pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setEditingMember(null)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={updateMember.isPending}>
                    {updateMember.isPending ? "Saving Changes..." : "Save Changes"}
                  </Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* 3. Member Detail Modal */}
        {/* ========================================================= */}
        <Dialog
          open={!!detailMember}
          onOpenChange={(open) => !open && setDetailMember(null)}
          className="max-w-3xl"
        >
          <DialogContent onClose={() => setDetailMember(null)} className="max-h-[90vh] overflow-y-auto">
            {detailMember && (
              <div className="space-y-6">
                {/* Header profile */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
                  <div className="flex items-center gap-3.5">
                    <div className="h-14 w-14 rounded-2xl bg-indigo-950/70 border border-indigo-800/50 text-indigo-400 flex items-center justify-center text-xl font-bold">
                      {detailMember.name.charAt(0)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h2 className="text-xl font-bold text-white">{detailMember.name}</h2>
                        <Badge
                          variant={detailMember.status === "active" ? "success" : "secondary"}
                          className="capitalize text-xs"
                        >
                          {detailMember.status}
                        </Badge>
                        {detailMember.is_at_risk && (
                          <Badge
                            variant="destructive"
                            className="text-xs bg-red-950 text-red-400 border border-red-800/60 flex items-center gap-1"
                          >
                            <AlertTriangle className="h-3 w-3" />
                            At Risk
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-zinc-400 mt-1 flex-wrap">
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3 text-zinc-500" />
                          {detailMember.email}
                        </span>
                        <span className="flex items-center gap-1">
                          <Phone className="h-3 w-3 text-zinc-500" />
                          {detailMember.phone}
                        </span>
                        {detailMember.city && (
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3 text-zinc-500" />
                            {detailMember.city}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1.5 self-start sm:self-auto"
                    onClick={() => {
                      const m = detailMember;
                      setDetailMember(null);
                      openEditModal(m);
                    }}
                  >
                    <Edit2 className="h-3.5 w-3.5" /> Edit Profile
                  </Button>
                </div>

                {/* Financial KPI Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Lifetime Value
                    </span>
                    <p className="text-lg font-bold font-mono text-emerald-400 mt-1">
                      {formatINR(detailMember.lifetime_value || 0)}
                    </p>
                    <span className="text-[10px] text-zinc-500">Cumulative revenue</span>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Total Payments
                    </span>
                    <p className="text-lg font-bold font-mono text-white mt-1">
                      {detailMember.total_payments || 0}
                    </p>
                    <span className="text-[10px] text-zinc-500">Recorded receipts</span>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Average Ticket
                    </span>
                    <p className="text-lg font-bold font-mono text-indigo-400 mt-1">
                      {formatINR(detailMember.average_payment || 0)}
                    </p>
                    <span className="text-[10px] text-zinc-500">Per payment avg</span>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Last Payment
                    </span>
                    <p className="text-xs font-semibold text-zinc-200 mt-1.5 truncate">
                      {detailMember.last_payment_date
                        ? formatDate(detailMember.last_payment_date)
                        : "No payments"}
                    </p>
                    <span className="text-[10px] text-zinc-500">Most recent transaction</span>
                  </div>
                </div>

                {/* Risk Alert (if at risk) */}
                {detailMember.is_at_risk && (
                  <div className="rounded-lg border border-red-900/50 bg-red-950/30 p-3.5 flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-xs font-bold text-red-300">Retention Alert: At Risk of Churn</h4>
                      <p className="text-xs text-red-200/80 mt-0.5">
                        {detailMember.risk_reason || "Expiring soon or has overdue payment requirements."}
                      </p>
                    </div>
                  </div>
                )}

                {/* 3 Detail Breakdown Sections */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Column 1: Demographics */}
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4 space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5 border-b border-zinc-800/80 pb-2">
                      <User className="h-3.5 w-3.5 text-indigo-400" /> Demographics
                    </h3>
                    <div className="space-y-2 text-xs">
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Age & Birthday</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.age != null
                            ? `${detailMember.age} yrs`
                            : computeAge(detailMember.date_of_birth) != null
                            ? `${computeAge(detailMember.date_of_birth)} yrs`
                            : "—"}{" "}
                          {detailMember.date_of_birth && (
                            <span className="text-zinc-400">
                              ({formatDate(detailMember.date_of_birth)})
                            </span>
                          )}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Gender</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.gender || "Not specified"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">City / Location</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.city || "Not specified"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Occupation</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.occupation || "Not specified"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Member Since</span>
                        <span className="text-zinc-200 font-medium">
                          {formatDate(detailMember.join_date)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Column 2: Fitness Profile */}
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4 space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5 border-b border-zinc-800/80 pb-2">
                      <Target className="h-3.5 w-3.5 text-indigo-400" /> Fitness Profile
                    </h3>
                    <div className="space-y-2 text-xs">
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Fitness Goal</span>
                        <span className="text-indigo-400 font-medium">
                          {detailMember.fitness_goal || "General Fitness"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Preferred Time</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.preferred_training_time || "Flexible"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Assigned Coach</span>
                        <span className="text-zinc-200 font-medium flex items-center gap-1">
                          <Dumbbell className="h-3 w-3 text-indigo-400" />
                          {detailMember.trainer_name || "Unassigned"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Acquisition Source</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.acquisition_source || "Walk-in"}
                        </span>
                      </div>
                      {detailMember.referral_source && (
                        <div>
                          <span className="text-zinc-500 block text-[11px]">Referral Note</span>
                          <span className="text-zinc-300">
                            {detailMember.referral_source}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Column 3: Membership Status */}
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4 space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5 border-b border-zinc-800/80 pb-2">
                      <Clock className="h-3.5 w-3.5 text-indigo-400" /> Subscription
                    </h3>
                    <div className="space-y-2 text-xs">
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Current Plan</span>
                        <span className="text-indigo-400 font-semibold">
                          {detailMember.membership_plan_name || "No active plan"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Contract Window</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.membership_start_date
                            ? `${formatDate(detailMember.membership_start_date)} — ${formatDate(
                                detailMember.membership_end_date
                              )}`
                            : "—"}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Renewals Logged</span>
                        <span className="text-zinc-200 font-medium">
                          {detailMember.renewal_count || 0} renewals
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 block text-[11px]">Retention Health</span>
                        {detailMember.is_at_risk ? (
                          <span className="text-red-400 font-medium flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" /> Needs Attention
                          </span>
                        ) : (
                          <span className="text-emerald-400 font-medium flex items-center gap-1">
                            <CheckCircle2 className="h-3 w-3" /> Healthy Standing
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <DialogFooter className="pt-2">
                  <Button variant="outline" onClick={() => setDetailMember(null)}>
                    Close
                  </Button>
                </DialogFooter>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* 4. Delete Confirmation Dialog */}
        {/* ========================================================= */}
        <Dialog
          open={!!deletingMember}
          onOpenChange={(open) => !open && setDeletingMember(null)}
        >
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
