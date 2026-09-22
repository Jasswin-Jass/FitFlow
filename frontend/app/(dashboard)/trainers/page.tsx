"use client";

import React, { useState } from "react";
import {
  Dumbbell,
  Plus,
  Mail,
  Phone,
  Award,
  Trash2,
  Edit2,
  User,
  Star,
  CheckCircle2,
  Users,
  TrendingUp,
  Clock,
  Briefcase,
  UserMinus,
  MessageSquare,
  Sparkles,
} from "lucide-react";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
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
  useTrainers,
  useCreateTrainer,
  useUpdateTrainer,
  useDeleteTrainer,
  useTrainerClients,
  useAssignTrainerClient,
  useUnassignTrainerClient,
  useTrainerReviews,
  useCreateTrainerReview,
} from "@/hooks/use-trainers";
import { useMembers } from "@/hooks/use-members";
import { useAuth } from "@/hooks/use-auth";
import { formatDate, formatINR } from "@/lib/utils";
import { Trainer, TrainerClientItem, TrainerReview, Member } from "@/types/api";

const initialTrainerForm = {
  name: "",
  email: "",
  phone: "",
  specialization: "General Fitness",
  years_of_experience: 2,
  certification: "",
  certification_level: "Certified Coach",
  max_client_capacity: 20,
  employment_type: "Full-time",
  status: "active" as "active" | "inactive",
  bio: "",
};

export default function TrainersPage() {
  const { user } = useAuth();
  const { data: trainersData, isLoading } = useTrainers();
  const { data: membersData } = useMembers({ size: 100 });

  const createTrainer = useCreateTrainer();
  const updateTrainer = useUpdateTrainer();
  const deleteTrainer = useDeleteTrainer();

  // Add Trainer State
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [addForm, setAddForm] = useState(initialTrainerForm);

  // Edit Trainer State
  const [editingTrainer, setEditingTrainer] = useState<Trainer | null>(null);
  const [editForm, setEditForm] = useState(initialTrainerForm);

  // Delete Confirmation State
  const [deletingTrainer, setDeletingTrainer] = useState<Trainer | null>(null);

  // Trainer Detail Modal State
  const [selectedTrainer, setSelectedTrainer] = useState<Trainer | null>(null);

  // Assign Client Modal State
  const [isAssignClientOpen, setIsAssignClientOpen] = useState(false);
  const [selectedMemberIdToAssign, setSelectedMemberIdToAssign] = useState("");

  // Add Review Modal State
  const [isAddReviewOpen, setIsAddReviewOpen] = useState(false);
  const [reviewForm, setReviewForm] = useState({
    member_id: "",
    rating: 5,
    review: "",
  });

  // Active sub-queries for selected trainer
  const { data: clientsData, isLoading: isLoadingClients } = useTrainerClients(selectedTrainer?.id);
  const { data: reviewsData, isLoading: isLoadingReviews } = useTrainerReviews(selectedTrainer?.id);

  const assignClientMutation = useAssignTrainerClient();
  const unassignClientMutation = useUnassignTrainerClient();
  const createReviewMutation = useCreateTrainerReview();

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createTrainer.mutateAsync({
      name: addForm.name.trim(),
      email: addForm.email.trim(),
      phone: addForm.phone.trim() || undefined,
      specialization: addForm.specialization,
      specialty: addForm.specialization,
      years_of_experience: Number(addForm.years_of_experience) || 0,
      certification: addForm.certification.trim() || undefined,
      certification_level: addForm.certification_level,
      max_client_capacity: Number(addForm.max_client_capacity) || 20,
      employment_type: addForm.employment_type,
      status: addForm.status,
      bio: addForm.bio.trim() || undefined,
    });
    setIsAddOpen(false);
    setAddForm(initialTrainerForm);
  };

  const openEditModal = (t: Trainer) => {
    setEditingTrainer(t);
    setEditForm({
      name: t.name || "",
      email: t.email || "",
      phone: t.phone || "",
      specialization: t.specialization || t.specialty || "General Fitness",
      years_of_experience: t.years_of_experience ?? (t as any).experience_years ?? 2,
      certification: t.certification || "",
      certification_level: t.certification_level || "Certified Coach",
      max_client_capacity: t.max_client_capacity || 20,
      employment_type: t.employment_type || "Full-time",
      status: (t.status as "active" | "inactive") || "active",
      bio: t.bio || "",
    });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTrainer) return;
    await updateTrainer.mutateAsync({
      id: editingTrainer.id,
      data: {
        name: editForm.name.trim(),
        email: editForm.email.trim(),
        phone: editForm.phone.trim() || undefined,
        specialization: editForm.specialization,
        specialty: editForm.specialization,
        years_of_experience: Number(editForm.years_of_experience) || 0,
        certification: editForm.certification.trim() || undefined,
        certification_level: editForm.certification_level,
        max_client_capacity: Number(editForm.max_client_capacity) || 20,
        employment_type: editForm.employment_type,
        status: editForm.status,
        bio: editForm.bio.trim() || undefined,
      },
    });
    setEditingTrainer(null);
  };

  const handleDelete = async () => {
    if (!deletingTrainer) return;
    await deleteTrainer.mutateAsync(deletingTrainer.id);
    setDeletingTrainer(null);
    if (selectedTrainer?.id === deletingTrainer.id) {
      setSelectedTrainer(null);
    }
  };

  const handleAssignClient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTrainer || !selectedMemberIdToAssign) return;
    await assignClientMutation.mutateAsync({
      trainerId: selectedTrainer.id,
      memberId: selectedMemberIdToAssign,
    });
    setIsAssignClientOpen(false);
    setSelectedMemberIdToAssign("");
  };

  const handleUnassignClient = async (memberId: string) => {
    if (!selectedTrainer) return;
    await unassignClientMutation.mutateAsync({
      trainerId: selectedTrainer.id,
      memberId,
    });
  };

  const handleCreateReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTrainer || !reviewForm.member_id) return;
    await createReviewMutation.mutateAsync({
      trainerId: selectedTrainer.id,
      data: {
        member_id: reviewForm.member_id,
        rating: Number(reviewForm.rating),
        review: reviewForm.review.trim() || undefined,
      },
    });
    setIsAddReviewOpen(false);
    setReviewForm({ member_id: "", rating: 5, review: "" });
  };

  // Sync selected trainer from trainersData when query updates
  const activeSelectedTrainer =
    trainersData?.items.find((t) => t.id === selectedTrainer?.id) || selectedTrainer;

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Trainer Directory"
        subtitle="Manage fitness coaches, track workload capacity, assign clients, and review feedback"
      />

      <main className="flex-1 p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="text-xs text-zinc-400">
            {trainersData?.total || 0} trainers registered under{" "}
            <span className="text-zinc-200 font-semibold">{user?.gym_name}</span>
          </div>

          <Button
            onClick={() => {
              setAddForm(initialTrainerForm);
              setIsAddOpen(true);
            }}
            size="sm"
            className="gap-2 bg-indigo-600 hover:bg-indigo-700 h-9"
          >
            <Plus className="h-4 w-4" /> Add Trainer
          </Button>
        </div>

        {/* Trainers Card Grid */}
        {isLoading ? (
          <div className="py-16 text-center text-zinc-500 text-sm">
            Loading trainer directory...
          </div>
        ) : !trainersData?.items || trainersData.items.length === 0 ? (
          <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-900/30 p-12 text-center">
            <Dumbbell className="mx-auto h-8 w-8 text-zinc-600 mb-2" />
            <h4 className="text-sm font-semibold text-zinc-200">No trainers registered yet</h4>
            <p className="text-xs text-zinc-500 mt-1">
              Add your gym&apos;s strength coaches and fitness instructors.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {trainersData.items.map((trainer: Trainer) => {
              const assignedCount = trainer.assigned_clients_count || 0;
              const maxCap = trainer.max_client_capacity || 20;
              const loadPercent =
                trainer.client_load_percent ??
                (maxCap > 0 ? Math.round((assignedCount / maxCap) * 100) : 0);
              const expYears = trainer.years_of_experience ?? (trainer as any).experience_years ?? 0;

              return (
                <Card
                  key={trainer.id}
                  className="border-zinc-800 bg-zinc-900/70 hover:border-zinc-700 transition-all p-5 flex flex-col justify-between"
                >
                  <div>
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-indigo-950/60 border border-indigo-800/40 text-indigo-400 flex items-center justify-center font-bold text-sm">
                          {trainer.name.charAt(0)}
                        </div>
                        <div>
                          <h3 className="font-semibold text-zinc-100 text-sm">{trainer.name}</h3>
                          <p className="text-xs text-zinc-400 flex items-center gap-1 mt-0.5">
                            <Mail className="h-3 w-3 text-zinc-500" />
                            {trainer.email}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-zinc-400 hover:text-white"
                          title="Edit Trainer"
                          onClick={() => openEditModal(trainer)}
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-zinc-400 hover:text-red-400"
                          title="Delete Trainer"
                          onClick={() => setDeletingTrainer(trainer)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>

                    {/* Meta badges */}
                    <div className="mt-3 flex items-center gap-1.5 flex-wrap">
                      <Badge variant="outline" className="text-[10px] bg-zinc-800/80 border-zinc-700/60 text-zinc-300">
                        {trainer.specialization || trainer.specialty || "Fitness"}
                      </Badge>
                      <Badge variant="outline" className="text-[10px] bg-indigo-950/40 border-indigo-800/40 text-indigo-300">
                        {trainer.employment_type || "Full-time"}
                      </Badge>
                      <Badge
                        variant={trainer.status === "active" ? "success" : "secondary"}
                        className="text-[10px]"
                      >
                        {trainer.status}
                      </Badge>
                    </div>

                    {/* Stats */}
                    <div className="mt-4 pt-3 border-t border-zinc-800/60 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1 text-zinc-300">
                          <Award className="h-3.5 w-3.5 text-indigo-400" />
                          <span>{expYears}y experience</span>
                        </div>
                        <div className="flex items-center gap-1">
                          {trainer.rating != null ? (
                            <span className="text-[11px] text-amber-400 font-mono font-bold flex items-center gap-0.5">
                              <Star className="h-3 w-3 fill-amber-400" />
                              {trainer.rating.toFixed(1)}
                              <span className="text-zinc-500 font-normal">
                                ({trainer.review_count || 0})
                              </span>
                            </span>
                          ) : (
                            <span className="text-[10px] text-zinc-500 italic">Not rated yet</span>
                          )}
                        </div>
                      </div>

                      {/* Workload */}
                      <div className="space-y-1 pt-1">
                        <div className="flex items-center justify-between text-[11px] text-zinc-400">
                          <span>
                            Assigned Clients:{" "}
                            <strong className="text-zinc-200 font-mono">{assignedCount}</strong> / {maxCap}
                          </span>
                          <span className="font-mono text-indigo-400">{loadPercent}% load</span>
                        </div>
                        <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              loadPercent >= 90
                                ? "bg-red-500"
                                : loadPercent >= 70
                                ? "bg-amber-500"
                                : "bg-indigo-500"
                            }`}
                            style={{ width: `${Math.min(100, loadPercent)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card Action */}
                  <div className="mt-5 pt-3 border-t border-zinc-800/60">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full text-xs gap-1.5 bg-zinc-900 border-zinc-800 hover:bg-zinc-800"
                      onClick={() => setSelectedTrainer(trainer)}
                    >
                      <Users className="h-3.5 w-3.5 text-indigo-400" /> View Details & Clients
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* ========================================================= */}
        {/* 1. Add Trainer Dialog */}
        {/* ========================================================= */}
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen} className="max-w-xl">
          <DialogContent onClose={() => setIsAddOpen(false)} className="max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Dumbbell className="h-5 w-5 text-indigo-400" />
                Add Fitness Trainer
              </DialogTitle>
              <DialogDescription>
                Register a new coach or instructor for {user?.gym_name}.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleCreate} className="space-y-4 pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1.5 sm:col-span-2">
                  <label className="text-xs font-medium text-zinc-300">
                    Full Name <span className="text-red-400">*</span>
                  </label>
                  <Input
                    required
                    placeholder="e.g. Vignesh Sundaram"
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
                    placeholder="vignesh@gym.com"
                    value={addForm.email}
                    onChange={(e) => setAddForm({ ...addForm, email: e.target.value })}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Phone Number</label>
                  <Input
                    placeholder="+91 98401 23456"
                    value={addForm.phone}
                    onChange={(e) => setAddForm({ ...addForm, phone: e.target.value })}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Specialization</label>
                  <select
                    value={addForm.specialization}
                    onChange={(e) => setAddForm({ ...addForm, specialization: e.target.value })}
                    className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="General Fitness">General Fitness</option>
                    <option value="Strength & Conditioning">Strength & Conditioning</option>
                    <option value="HIIT & Cardio">HIIT & Cardio</option>
                    <option value="CrossFit">CrossFit</option>
                    <option value="Powerlifting">Powerlifting</option>
                    <option value="Yoga & Mobility">Yoga & Mobility</option>
                    <option value="Bodybuilding">Bodybuilding & Hypertrophy</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Experience (Years)</label>
                  <Input
                    type="number"
                    min={0}
                    max={50}
                    value={addForm.years_of_experience}
                    onChange={(e) =>
                      setAddForm({ ...addForm, years_of_experience: Number(e.target.value) })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Certification</label>
                  <Input
                    placeholder="e.g. ACE-CPT, NASM, ISSA, CSCS"
                    value={addForm.certification}
                    onChange={(e) => setAddForm({ ...addForm, certification: e.target.value })}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Certification Level</label>
                  <select
                    value={addForm.certification_level}
                    onChange={(e) =>
                      setAddForm({ ...addForm, certification_level: e.target.value })
                    }
                    className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="Certified Coach">Certified Coach</option>
                    <option value="Senior Instructor">Senior Instructor</option>
                    <option value="Master Trainer">Master Trainer</option>
                    <option value="Level 1">Level 1</option>
                    <option value="Level 2">Level 2</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Max Client Capacity</label>
                  <Input
                    type="number"
                    min={1}
                    max={100}
                    value={addForm.max_client_capacity}
                    onChange={(e) =>
                      setAddForm({ ...addForm, max_client_capacity: Number(e.target.value) })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Employment Type</label>
                  <select
                    value={addForm.employment_type}
                    onChange={(e) => setAddForm({ ...addForm, employment_type: e.target.value })}
                    className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Status</label>
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

                <div className="space-y-1.5 sm:col-span-2">
                  <label className="text-xs font-medium text-zinc-300">Coach Bio & Background</label>
                  <textarea
                    rows={3}
                    placeholder="Short biography, coaching style, personal athletic achievements..."
                    value={addForm.bio}
                    onChange={(e) => setAddForm({ ...addForm, bio: e.target.value })}
                    className="w-full rounded-md border border-zinc-700/60 bg-zinc-900/80 p-2.5 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
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
                <Button type="submit" disabled={createTrainer.isPending}>
                  {createTrainer.isPending ? "Adding Coach..." : "Add Trainer"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* 2. Edit Trainer Dialog */}
        {/* ========================================================= */}
        <Dialog
          open={!!editingTrainer}
          onOpenChange={(open) => !open && setEditingTrainer(null)}
          className="max-w-xl"
        >
          <DialogContent onClose={() => setEditingTrainer(null)} className="max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Edit2 className="h-5 w-5 text-indigo-400" />
                Edit Trainer Details
              </DialogTitle>
              <DialogDescription>
                Update coach credentials, capacity limits, and employment status.
              </DialogDescription>
            </DialogHeader>

            {editingTrainer && (
              <form onSubmit={handleUpdate} className="space-y-4 pt-2">
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
                    <label className="text-xs font-medium text-zinc-300">Phone Number</label>
                    <Input
                      value={editForm.phone}
                      onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Specialization</label>
                    <select
                      value={editForm.specialization}
                      onChange={(e) => setEditForm({ ...editForm, specialization: e.target.value })}
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="General Fitness">General Fitness</option>
                      <option value="Strength & Conditioning">Strength & Conditioning</option>
                      <option value="HIIT & Cardio">HIIT & Cardio</option>
                      <option value="CrossFit">CrossFit</option>
                      <option value="Powerlifting">Powerlifting</option>
                      <option value="Yoga & Mobility">Yoga & Mobility</option>
                      <option value="Bodybuilding">Bodybuilding & Hypertrophy</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Experience (Years)</label>
                    <Input
                      type="number"
                      min={0}
                      max={50}
                      value={editForm.years_of_experience}
                      onChange={(e) =>
                        setEditForm({ ...editForm, years_of_experience: Number(e.target.value) })
                      }
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Certification</label>
                    <Input
                      value={editForm.certification}
                      onChange={(e) => setEditForm({ ...editForm, certification: e.target.value })}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Certification Level</label>
                    <select
                      value={editForm.certification_level}
                      onChange={(e) =>
                        setEditForm({ ...editForm, certification_level: e.target.value })
                      }
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="Certified Coach">Certified Coach</option>
                      <option value="Senior Instructor">Senior Instructor</option>
                      <option value="Master Trainer">Master Trainer</option>
                      <option value="Level 1">Level 1</option>
                      <option value="Level 2">Level 2</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Max Client Capacity</label>
                    <Input
                      type="number"
                      min={1}
                      max={100}
                      value={editForm.max_client_capacity}
                      onChange={(e) =>
                        setEditForm({ ...editForm, max_client_capacity: Number(e.target.value) })
                      }
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Employment Type</label>
                    <select
                      value={editForm.employment_type}
                      onChange={(e) => setEditForm({ ...editForm, employment_type: e.target.value })}
                      className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-300">Status</label>
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

                  <div className="space-y-1.5 sm:col-span-2">
                    <label className="text-xs font-medium text-zinc-300">Coach Bio & Background</label>
                    <textarea
                      rows={3}
                      value={editForm.bio}
                      onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                      className="w-full rounded-md border border-zinc-700/60 bg-zinc-900/80 p-2.5 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                <DialogFooter className="pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setEditingTrainer(null)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={updateTrainer.isPending}>
                    {updateTrainer.isPending ? "Saving..." : "Save Changes"}
                  </Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* 3. Trainer Detail Modal (Profile, Clients, Reviews) */}
        {/* ========================================================= */}
        <Dialog
          open={!!activeSelectedTrainer}
          onOpenChange={(open) => !open && setSelectedTrainer(null)}
          className="max-w-4xl"
        >
          <DialogContent onClose={() => setSelectedTrainer(null)} className="max-h-[90vh] overflow-y-auto">
            {activeSelectedTrainer && (
              <div className="space-y-6">
                {/* Header Profile */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
                  <div className="flex items-center gap-3.5">
                    <div className="h-14 w-14 rounded-2xl bg-indigo-950/70 border border-indigo-800/50 text-indigo-400 flex items-center justify-center text-xl font-bold">
                      {activeSelectedTrainer.name.charAt(0)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h2 className="text-xl font-bold text-white">{activeSelectedTrainer.name}</h2>
                        <Badge
                          variant={activeSelectedTrainer.status === "active" ? "success" : "secondary"}
                          className="capitalize text-xs"
                        >
                          {activeSelectedTrainer.status}
                        </Badge>
                        <Badge variant="outline" className="text-xs text-indigo-300 border-indigo-800/50">
                          {activeSelectedTrainer.employment_type || "Full-time"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-zinc-400 mt-1 flex-wrap">
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3 text-zinc-500" />
                          {activeSelectedTrainer.email}
                        </span>
                        {activeSelectedTrainer.phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="h-3 w-3 text-zinc-500" />
                            {activeSelectedTrainer.phone}
                          </span>
                        )}
                        <span className="flex items-center gap-1 text-zinc-300">
                          <Award className="h-3 w-3 text-indigo-400" />
                          {activeSelectedTrainer.specialization || activeSelectedTrainer.specialty || "Fitness"} •{" "}
                          {activeSelectedTrainer.years_of_experience ??
                            (activeSelectedTrainer as any).experience_years ??
                            0}
                          y exp
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="gap-1.5"
                      onClick={() => {
                        const tr = activeSelectedTrainer;
                        setSelectedTrainer(null);
                        openEditModal(tr);
                      }}
                    >
                      <Edit2 className="h-3.5 w-3.5" /> Edit Profile
                    </Button>
                  </div>
                </div>

                {/* Bio text if provided */}
                {activeSelectedTrainer.bio && (
                  <div className="rounded-lg border border-zinc-800 bg-zinc-950/40 p-3 text-xs text-zinc-300 italic">
                    &ldquo;{activeSelectedTrainer.bio}&rdquo;
                  </div>
                )}

                {/* 4 Performance KPI cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Active Clients
                    </span>
                    <p className="text-lg font-bold font-mono text-white mt-1">
                      {activeSelectedTrainer.assigned_clients_count || 0}{" "}
                      <span className="text-xs text-zinc-500 font-normal">
                        / {activeSelectedTrainer.max_client_capacity} max
                      </span>
                    </p>
                    <span className="text-[10px] text-zinc-500">Current direct assignments</span>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Capacity Utilization
                    </span>
                    <p className="text-lg font-bold font-mono text-indigo-400 mt-1">
                      {activeSelectedTrainer.client_load_percent || 0}%
                    </p>
                    <span className="text-[10px] text-zinc-500">Roster load efficiency</span>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Client Rating
                    </span>
                    <p className="text-lg font-bold font-mono text-amber-400 mt-1 flex items-center gap-1">
                      {activeSelectedTrainer.rating != null ? (
                        <>
                          <Star className="h-4 w-4 fill-amber-400" />
                          {activeSelectedTrainer.rating.toFixed(1)}
                        </>
                      ) : (
                        <span className="text-xs text-zinc-500 italic font-normal">Not rated yet</span>
                      )}
                    </p>
                    <span className="text-[10px] text-zinc-500">
                      {activeSelectedTrainer.review_count || 0} verified reviews
                    </span>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block font-medium">
                      Revenue Generated
                    </span>
                    <p className="text-lg font-bold font-mono text-emerald-400 mt-1">
                      {formatINR(activeSelectedTrainer.revenue_generated || 0)}
                    </p>
                    <span className="text-[10px] text-zinc-500">From assigned members</span>
                  </div>
                </div>

                {/* Section A: Assigned Clients */}
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                        <Users className="h-4 w-4 text-indigo-400" /> Assigned Clients (
                        {clientsData?.total || 0})
                      </h3>
                      <p className="text-xs text-zinc-400">
                        Gym members currently working under {activeSelectedTrainer.name}&apos;s direct coaching
                      </p>
                    </div>

                    <Button
                      size="sm"
                      onClick={() => setIsAssignClientOpen(true)}
                      className="gap-1.5 bg-indigo-600 hover:bg-indigo-700 h-8 text-xs"
                    >
                      <Plus className="h-3.5 w-3.5" /> Assign Client
                    </Button>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 overflow-hidden">
                    <Table>
                      <TableHeader>
                        <TableRow className="border-zinc-800 bg-zinc-900/90 text-xs">
                          <TableHead>Member</TableHead>
                          <TableHead>Demographics</TableHead>
                          <TableHead>Current Plan</TableHead>
                          <TableHead>Expiry Date</TableHead>
                          <TableHead>Assigned On</TableHead>
                          <TableHead className="text-right">Action</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {isLoadingClients ? (
                          <TableRow>
                            <TableCell colSpan={6} className="text-center py-6 text-xs text-zinc-500">
                              Loading assigned clients...
                            </TableCell>
                          </TableRow>
                        ) : !clientsData?.items || clientsData.items.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={6} className="text-center py-8 text-xs text-zinc-500">
                              No clients currently assigned to this coach. Click &quot;Assign Client&quot; above.
                            </TableCell>
                          </TableRow>
                        ) : (
                          clientsData.items.map((client: TrainerClientItem) => (
                            <TableRow key={client.member_id} className="border-zinc-800/60 text-xs">
                              <TableCell className="font-medium text-white">
                                <div>
                                  <span className="block font-medium text-zinc-100">
                                    {client.name}
                                  </span>
                                  <span className="block text-[11px] text-zinc-400">
                                    {client.email}
                                  </span>
                                </div>
                              </TableCell>

                              <TableCell>
                                <span className="text-zinc-300">
                                  {client.gender || "—"} {client.age ? `• ${client.age}y` : ""}
                                </span>
                              </TableCell>

                              <TableCell>
                                {client.membership_plan_name ? (
                                  <Badge variant="outline" className="text-[11px] text-indigo-300 border-indigo-800/40">
                                    {client.membership_plan_name}
                                  </Badge>
                                ) : (
                                  <span className="text-zinc-500 italic">No plan</span>
                                )}
                              </TableCell>

                              <TableCell className="text-zinc-400">
                                {formatDate(client.membership_end_date)}
                              </TableCell>

                              <TableCell className="text-zinc-500">
                                {formatDate(client.assigned_at)}
                              </TableCell>

                              <TableCell className="text-right">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 text-xs text-red-400 hover:text-red-300 hover:bg-red-950/30 gap-1"
                                  onClick={() => handleUnassignClient(client.member_id)}
                                  disabled={unassignClientMutation.isPending}
                                >
                                  <UserMinus className="h-3 w-3" /> Unassign
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>

                {/* Section B: Reviews & Feedback */}
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 text-indigo-400" /> Member Reviews (
                        {reviewsData?.total || 0})
                      </h3>
                      <p className="text-xs text-zinc-400">
                        Ratings and testimonials submitted by gym members
                      </p>
                    </div>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setIsAddReviewOpen(true)}
                      className="gap-1.5 border-zinc-700 h-8 text-xs"
                    >
                      <Star className="h-3.5 w-3.5 text-amber-400" /> Add Review
                    </Button>
                  </div>

                  <div className="space-y-2.5">
                    {isLoadingReviews ? (
                      <div className="text-center py-6 text-xs text-zinc-500">
                        Loading member reviews...
                      </div>
                    ) : !reviewsData?.items || reviewsData.items.length === 0 ? (
                      <div className="rounded-xl border border-dashed border-zinc-800 p-6 text-center text-xs text-zinc-500">
                        No reviews submitted yet for this trainer. Click &quot;Add Review&quot; to log feedback.
                      </div>
                    ) : (
                      reviewsData.items.map((rev: TrainerReview) => (
                        <div
                          key={rev.id}
                          className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-3.5 space-y-1.5"
                        >
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-semibold text-zinc-200">
                              {rev.member_name || "Gym Member"}
                            </span>
                            <div className="flex items-center gap-1 font-mono text-amber-400 font-bold text-xs">
                              {Array.from({ length: 5 }).map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-3 w-3 ${
                                    i < rev.rating
                                      ? "fill-amber-400 text-amber-400"
                                      : "text-zinc-700"
                                  }`}
                                />
                              ))}
                              <span className="ml-1 text-[11px] text-zinc-400">
                                {formatDate(rev.created_at)}
                              </span>
                            </div>
                          </div>
                          {rev.review && (
                            <p className="text-xs text-zinc-300 leading-relaxed">
                              &ldquo;{rev.review}&rdquo;
                            </p>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <DialogFooter className="pt-2">
                  <Button variant="outline" onClick={() => setSelectedTrainer(null)}>
                    Close
                  </Button>
                </DialogFooter>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* Submodal 1: Assign Client Modal */}
        {/* ========================================================= */}
        <Dialog open={isAssignClientOpen} onOpenChange={setIsAssignClientOpen}>
          <DialogContent onClose={() => setIsAssignClientOpen(false)}>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-indigo-400" />
                Assign Member to {activeSelectedTrainer?.name}
              </DialogTitle>
              <DialogDescription>
                Select an active gym member to assign under this coach.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleAssignClient} className="space-y-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Select Member</label>
                <select
                  required
                  value={selectedMemberIdToAssign}
                  onChange={(e) => setSelectedMemberIdToAssign(e.target.value)}
                  className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="">-- Choose Member --</option>
                  {membersData?.items.map((m: Member) => (
                    <option key={m.id} value={m.id}>
                      {m.name} ({m.email}) {m.membership_plan_name ? `• ${m.membership_plan_name}` : ""}
                    </option>
                  ))}
                </select>
              </div>

              <DialogFooter className="pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsAssignClientOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={!selectedMemberIdToAssign || assignClientMutation.isPending}
                >
                  {assignClientMutation.isPending ? "Assigning..." : "Confirm Assignment"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* Submodal 2: Add Review Modal */}
        {/* ========================================================= */}
        <Dialog open={isAddReviewOpen} onOpenChange={setIsAddReviewOpen}>
          <DialogContent onClose={() => setIsAddReviewOpen(false)}>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-amber-400" />
                Add Review for {activeSelectedTrainer?.name}
              </DialogTitle>
              <DialogDescription>
                Submit member rating and testimonial for this trainer.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleCreateReview} className="space-y-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Reviewing Member</label>
                <select
                  required
                  value={reviewForm.member_id}
                  onChange={(e) => setReviewForm({ ...reviewForm, member_id: e.target.value })}
                  className="w-full h-9 rounded-md border border-zinc-700/60 bg-zinc-900/80 px-3 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
                <label className="text-xs font-medium text-zinc-300">Rating (1 to 5 Stars)</label>
                <div className="flex items-center gap-2 pt-1">
                  {[1, 2, 3, 4, 5].map((starVal) => (
                    <button
                      type="button"
                      key={starVal}
                      onClick={() => setReviewForm({ ...reviewForm, rating: starVal })}
                      className="p-1 hover:scale-110 transition-transform"
                    >
                      <Star
                        className={`h-6 w-6 ${
                          starVal <= reviewForm.rating
                            ? "fill-amber-400 text-amber-400"
                            : "text-zinc-700"
                        }`}
                      />
                    </button>
                  ))}
                  <span className="text-xs font-mono text-zinc-300 ml-2">
                    {reviewForm.rating} / 5 Stars
                  </span>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Review Notes / Testimonial</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Great coaching form corrections, very attentive and motivating!"
                  value={reviewForm.review}
                  onChange={(e) => setReviewForm({ ...reviewForm, review: e.target.value })}
                  className="w-full rounded-md border border-zinc-700/60 bg-zinc-900/80 p-2.5 text-xs text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <DialogFooter className="pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsAddReviewOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={!reviewForm.member_id || createReviewMutation.isPending}
                >
                  {createReviewMutation.isPending ? "Submitting..." : "Submit Review"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* ========================================================= */}
        {/* 4. Delete Confirmation Dialog */}
        {/* ========================================================= */}
        <Dialog open={!!deletingTrainer} onOpenChange={(open) => !open && setDeletingTrainer(null)}>
          <DialogContent onClose={() => setDeletingTrainer(null)}>
            <DialogHeader>
              <DialogTitle className="text-red-400">Delete Trainer</DialogTitle>
              <DialogDescription>
                Are you sure you want to remove{" "}
                <strong className="text-zinc-100">{deletingTrainer?.name}</strong> from your
                staff directory? Member assignments will be unlinked.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setDeletingTrainer(null)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={deleteTrainer.isPending}
              >
                {deleteTrainer.isPending ? "Removing..." : "Remove"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
