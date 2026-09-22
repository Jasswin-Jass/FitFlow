"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Building2, User, Mail, Lock, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";

export default function RegisterPage() {
  const { register, isRegistering, registerError } = useAuth();
  const [gymName, setGymName] = useState("");
  const [ownerName, setOwnerName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register({
        gym_name: gymName,
        owner_name: ownerName,
        email,
        password,
      });
    } catch {
      // Handled by hook
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 font-bold text-white shadow-lg shadow-indigo-600/30 mb-3">
            FF
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Register New Gym
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Create an isolated tenant environment for your fitness business
          </p>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900/80 p-6 shadow-xl backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            {registerError && (
              <div className="rounded-lg border border-red-900/50 bg-red-950/40 p-3 text-xs text-red-300">
                {registerError.detail || "Registration failed. Please check inputs."}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">Gym Name</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                <Input
                  required
                  placeholder="e.g. Titan Fitness Club"
                  className="pl-9"
                  value={gymName}
                  onChange={(e) => setGymName(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">Owner Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                <Input
                  required
                  placeholder="e.g. Anand Mahindra"
                  className="pl-9"
                  value={ownerName}
                  onChange={(e) => setOwnerName(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">Work Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                <Input
                  type="email"
                  required
                  placeholder="owner@titanfitness.com"
                  className="pl-9"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                <Input
                  type="password"
                  required
                  placeholder="At least 6 characters"
                  className="pl-9"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={isRegistering}
              className="w-full h-10 gap-2 font-semibold"
            >
              {isRegistering ? "Provisioning Tenant..." : "Create Gym & Open Dashboard"}
              {!isRegistering && <ArrowRight className="h-4 w-4" />}
            </Button>
          </form>

          <div className="mt-6 text-center text-xs text-zinc-400">
            Already have a gym registered?{" "}
            <Link
              href="/login"
              className="font-medium text-indigo-400 hover:text-indigo-300 underline underline-offset-4"
            >
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
