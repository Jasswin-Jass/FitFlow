"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Lock, Mail, ArrowRight, Building2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";

export default function LoginPage() {
  const { login, isLoggingIn, loginError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login({ email, password });
    } catch {
      // Error handled by hook
    }
  };

  const handleQuickDemo = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    login({ email: demoEmail, password: demoPass });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 font-bold text-white shadow-lg shadow-indigo-600/30 mb-3">
            FF
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            FitFlow
          </h1>
          <p className="text-xs font-semibold uppercase tracking-wider text-indigo-400 mt-0.5">
            Business Intelligence Platform for Gyms
          </p>
          <p className="text-sm text-zinc-400 mt-2">
            Sign in to access your gym&apos;s executive metrics
          </p>
        </div>

        {/* Demo Quick-Switch Helper */}
        <div className="rounded-xl border border-indigo-900/40 bg-indigo-950/20 p-4">
          <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-indigo-300">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Hackathon Demo One-Click Sign-In:</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() =>
                handleQuickDemo("karthik.ramesh@fitcorefitness.com", "FitCore@2026")
              }
              className="flex flex-col text-left p-2.5 rounded-lg border border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 hover:border-indigo-600 transition-all text-xs"
            >
              <span className="font-semibold text-zinc-100 flex items-center gap-1">
                <Building2 className="h-3 w-3 text-indigo-400" /> FitCore (Gym A)
              </span>
              <span className="text-[10px] text-zinc-400 mt-0.5">Seeded with 18 members</span>
            </button>

            <button
              type="button"
              onClick={() =>
                handleQuickDemo("arjun.kumar@urbanstrength.in", "Urban@2026")
              }
              className="flex flex-col text-left p-2.5 rounded-lg border border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 hover:border-indigo-600 transition-all text-xs"
            >
              <span className="font-semibold text-zinc-100 flex items-center gap-1">
                <Building2 className="h-3 w-3 text-indigo-400" /> Urban Strength (Gym B)
              </span>
              <span className="text-[10px] text-zinc-400 mt-0.5">Isolated tenant demo</span>
            </button>
          </div>
        </div>

        {/* Login Form */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/80 p-6 shadow-xl backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            {loginError && (
              <div className="rounded-lg border border-red-900/50 bg-red-950/40 p-3 text-xs text-red-300">
                {loginError.detail || "Invalid email or password"}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">
                Account Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                <Input
                  type="email"
                  required
                  placeholder="owner@gym.com"
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
                  placeholder="••••••••"
                  className="pl-9"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoggingIn}
              className="w-full h-10 gap-2 font-semibold"
            >
              {isLoggingIn ? "Authenticating..." : "Sign In to FitFlow"}
              {!isLoggingIn && <ArrowRight className="h-4 w-4" />}
            </Button>
          </form>

          <div className="mt-6 text-center text-xs text-zinc-400">
            Need to register a new gym?{" "}
            <Link
              href="/register"
              className="font-medium text-indigo-400 hover:text-indigo-300 underline underline-offset-4"
            >
              Create gym account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
