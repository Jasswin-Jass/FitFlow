"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  LineChart,
  Users,
  CreditCard,
  UserCheck,
  Dumbbell,
  LogOut,
  Building2,
} from "lucide-react";
import { useAuth } from "@/hooks/use-auth";

const navigation = [
  {
    section: "Business Intelligence",
    items: [
      { name: "Executive Summary", href: "/dashboard", icon: BarChart3 },
      { name: "Deep-Dive Analytics", href: "/analytics", icon: LineChart },
    ],
  },
  {
    section: "Operations",
    items: [
      { name: "Members", href: "/members", icon: Users },
      { name: "Memberships", href: "/memberships", icon: UserCheck },
      { name: "Payments", href: "/payments", icon: CreditCard },
      { name: "Trainers", href: "/trainers", icon: Dumbbell },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-zinc-800/80 bg-zinc-950 text-zinc-300">
      {/* Brand Header */}
      <div className="flex h-16 items-center gap-3 border-b border-zinc-800/80 px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 font-bold text-white shadow-md shadow-indigo-600/30">
          FF
        </div>
        <div>
          <span className="text-base font-bold tracking-tight text-white">
            FitFlow
          </span>
          <span className="block text-[10px] font-medium uppercase tracking-wider text-indigo-400">
            Business Intelligence
          </span>
        </div>
      </div>

      {/* Gym Badge */}
      <div className="px-4 py-3 border-b border-zinc-900 bg-zinc-900/40">
        <div className="flex items-center gap-2 rounded-md bg-zinc-900/90 px-3 py-2 border border-zinc-800/60">
          <Building2 className="h-4 w-4 text-indigo-400 shrink-0" />
          <div className="truncate">
            <p className="text-xs font-semibold text-zinc-100 truncate">
              {user?.gym_name || "FitFlow Gym"}
            </p>
            <p className="text-[10px] text-zinc-400 capitalize">
              Role: {user?.role || "Owner"}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4">
        {navigation.map((group) => (
          <div key={group.section} className="space-y-1">
            <h4 className="px-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
              {group.section}
            </h4>
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                      isActive
                        ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/20"
                        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
                    }`}
                  >
                    <Icon
                      className={`h-4 w-4 shrink-0 transition-colors ${
                        isActive ? "text-white" : "text-zinc-400 group-hover:text-zinc-200"
                      }`}
                    />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* User Footer & Logout */}
      <div className="border-t border-zinc-800/80 p-3">
        <div className="flex items-center justify-between rounded-lg bg-zinc-900/60 p-2.5">
          <div className="truncate pr-2">
            <p className="text-xs font-medium text-zinc-200 truncate">
              {user?.email || "Gym Owner"}
            </p>
            <p className="text-[10px] text-zinc-400 truncate">Authenticated session</p>
          </div>
          <button
            onClick={logout}
            title="Log out"
            className="flex h-8 w-8 items-center justify-center rounded-md text-zinc-400 hover:bg-zinc-800 hover:text-red-400 transition-colors"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
