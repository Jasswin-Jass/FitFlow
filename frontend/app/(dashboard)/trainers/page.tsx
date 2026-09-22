"use client";

import React, { useState } from "react";
import { Dumbbell, Plus, Mail, Award, Trash2, Edit2, User } from "lucide-react";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
} from "@/hooks/use-trainers";
import { useAuth } from "@/hooks/use-auth";
import { Trainer } from "@/types/api";

export default function TrainersPage() {
  const { user } = useAuth();
  const { data: trainersData, isLoading } = useTrainers();
  const createTrainer = useCreateTrainer();
  const updateTrainer = useUpdateTrainer();
  const deleteTrainer = useDeleteTrainer();

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    specialty: "",
  });

  const [editingTrainer, setEditingTrainer] = useState<Trainer | null>(null);
  const [deletingTrainer, setDeletingTrainer] = useState<Trainer | null>(null);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createTrainer.mutateAsync(form);
    setIsAddOpen(false);
    setForm({ name: "", email: "", specialty: "" });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTrainer) return;
    await updateTrainer.mutateAsync({
      id: editingTrainer.id,
      data: {
        name: editingTrainer.name,
        email: editingTrainer.email,
        specialty: editingTrainer.specialty,
      },
    });
    setEditingTrainer(null);
  };

  const handleDelete = async () => {
    if (!deletingTrainer) return;
    await deleteTrainer.mutateAsync(deletingTrainer.id);
    setDeletingTrainer(null);
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Trainer Directory"
        subtitle="Manage fitness coaches, instructors, and specialty certifications"
      />

      <main className="flex-1 p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="text-xs text-zinc-400">
            {trainersData?.total || 0} trainers registered under{" "}
            <span className="text-zinc-200 font-semibold">{user?.gym_name}</span>
          </div>

          <Button
            onClick={() => setIsAddOpen(true)}
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
            {trainersData.items.map((trainer: Trainer) => (
              <Card
                key={trainer.id}
                className="border-zinc-800 bg-zinc-900/70 hover:border-zinc-700 transition-all p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-indigo-950/60 border border-indigo-800/40 text-indigo-400 flex items-center justify-center font-bold text-sm">
                        {trainer.name.charAt(0)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-zinc-100 text-sm">
                          {trainer.name}
                        </h3>
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
                        onClick={() => setEditingTrainer(trainer)}
                      >
                        <Edit2 className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-zinc-400 hover:text-red-400"
                        onClick={() => setDeletingTrainer(trainer)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-zinc-800/60 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5 text-indigo-300">
                        <Award className="h-3.5 w-3.5 text-indigo-400" />
                        <span className="font-medium truncate max-w-[130px]">{trainer.specialty}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-[10px] text-amber-400 font-mono font-bold">
                          {trainer.rating ? trainer.rating.toFixed(1) : "5.0"} ★
                        </span>
                        <span className="text-[10px] text-zinc-500">• {trainer.years_of_experience || 0}y exp</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-zinc-400 pt-1">
                      <span>Clients: <strong className="text-zinc-200 font-mono">{trainer.assigned_clients_count || 0}</strong> / {trainer.max_client_capacity}</span>
                      <span className="font-mono text-indigo-400">{trainer.client_load_percent || 0}% load</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* 1. Add Trainer Dialog */}
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogContent onClose={() => setIsAddOpen(false)}>
            <DialogHeader>
              <DialogTitle>Add Fitness Trainer</DialogTitle>
              <DialogDescription>
                Register a new coach or instructor for {user?.gym_name}.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Trainer Name</label>
                <Input
                  required
                  placeholder="e.g. Vignesh Sundaram"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Email</label>
                <Input
                  type="email"
                  required
                  placeholder="vignesh@gym.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">Specialty</label>
                <Input
                  required
                  placeholder="e.g. Strength & Conditioning, CrossFit, Yoga"
                  value={form.specialty}
                  onChange={(e) => setForm({ ...form, specialty: e.target.value })}
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
                <Button type="submit" disabled={createTrainer.isPending}>
                  {createTrainer.isPending ? "Adding..." : "Add Trainer"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* 2. Edit Trainer Dialog */}
        <Dialog open={!!editingTrainer} onOpenChange={(open) => !open && setEditingTrainer(null)}>
          <DialogContent onClose={() => setEditingTrainer(null)}>
            <DialogHeader>
              <DialogTitle>Edit Trainer</DialogTitle>
              <DialogDescription>Update coach details and specialties.</DialogDescription>
            </DialogHeader>

            {editingTrainer && (
              <form onSubmit={handleUpdate} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Trainer Name</label>
                  <Input
                    required
                    value={editingTrainer.name}
                    onChange={(e) =>
                      setEditingTrainer({ ...editingTrainer, name: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Email</label>
                  <Input
                    type="email"
                    required
                    value={editingTrainer.email}
                    onChange={(e) =>
                      setEditingTrainer({ ...editingTrainer, email: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-300">Specialty</label>
                  <Input
                    required
                    value={editingTrainer.specialty}
                    onChange={(e) =>
                      setEditingTrainer({ ...editingTrainer, specialty: e.target.value })
                    }
                  />
                </div>

                <DialogFooter>
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

        {/* 3. Delete Trainer Dialog */}
        <Dialog open={!!deletingTrainer} onOpenChange={(open) => !open && setDeletingTrainer(null)}>
          <DialogContent onClose={() => setDeletingTrainer(null)}>
            <DialogHeader>
              <DialogTitle className="text-red-400">Delete Trainer</DialogTitle>
              <DialogDescription>
                Are you sure you want to remove{" "}
                <strong className="text-zinc-100">{deletingTrainer?.name}</strong> from your
                staff directory?
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
