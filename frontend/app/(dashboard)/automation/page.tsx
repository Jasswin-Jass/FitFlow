"use client";

import React, { useState } from "react";
import {
  Zap,
  Play,
  RotateCw,
  Bell,
  CheckCircle2,
  AlertCircle,
  Clock,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  Info,
  Server,
  Mail,
  MessageSquare,
} from "lucide-react";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
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
  useAutomationStatus,
  useProcessDuePayments,
  usePaymentReminders,
  useTriggerChecks,
} from "@/hooks/use-payments";
import { formatDate, formatINR } from "@/lib/utils";
import { DuePaymentsProcessResponse } from "@/types/api";

export default function AutomationPage() {
  const { data: statusData, isLoading: isStatusLoading } = useAutomationStatus();
  const { data: remindersData, isLoading: isRemindersLoading } = usePaymentReminders();
  const processDuePayments = useProcessDuePayments();
  const triggerChecks = useTriggerChecks();

  const [lastBatchResult, setLastBatchResult] = useState<DuePaymentsProcessResponse | null>(null);

  const handleRunBatch = async () => {
    const res = await processDuePayments.mutateAsync();
    setLastBatchResult(res);
  };

  const handleTriggerChecks = async () => {
    await triggerChecks.mutateAsync();
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-zinc-950 text-zinc-100">
      <Header
        title="Billing & Payment Automation"
        subtitle="Automated recurring renewal mandates, cron batch payment runner, and reminder audit logs"
      />

      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Architecture Notice Banner */}
        <div className="rounded-xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 via-zinc-900/60 to-purple-950/30 p-5 shadow-sm">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shrink-0">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-white text-sm">
                    Decoupled Provider Architecture Active
                  </h3>
                  <Badge variant="outline" className="text-[10px] text-emerald-400 border-emerald-500/30 bg-emerald-500/10">
                    Demo Mode Active
                  </Badge>
                </div>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Business logic is 100% provider-agnostic. The server-side <code className="text-indigo-300 font-mono">PaymentProvider</code> interface allows seamless drop-in of live Razorpay UPI / Mandates without altering subscriptions or billing rules.
                </p>
              </div>
            </div>

            <Button
              onClick={handleTriggerChecks}
              disabled={triggerChecks.isPending}
              variant="outline"
              size="sm"
              className="text-xs border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/10 shrink-0"
            >
              <RotateCw className={`h-3.5 w-3.5 mr-1.5 ${triggerChecks.isPending ? "animate-spin" : ""}`} />
              Run Reminder Rule Evaluation
            </Button>
          </div>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Active Mandates</span>
              <div className="h-8 w-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <Zap className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-2xl font-bold font-mono text-zinc-100">
              {statusData?.active_subscriptions_count ?? "..."}
            </div>
            <p className="mt-1 text-xs text-zinc-500">Members with recurring auto-renewal</p>
          </div>

          <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Auto-Renewal Provider</span>
              <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                <Server className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-lg font-bold text-emerald-400">
              {statusData?.provider ?? "Demo Provider"}
            </div>
            <p className="mt-1 text-xs text-zinc-500">Autonomous tokenized billing</p>
          </div>

          <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Monthly Projected MRR</span>
              <div className="h-8 w-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
                <Layers className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-2xl font-bold font-mono text-purple-400">
              {formatINR(statusData?.total_collected_monthly ?? 0)}
            </div>
            <p className="mt-1 text-xs text-zinc-500">Secured via active renewal mandates</p>
          </div>

          <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Reminder Rules</span>
              <div className="h-8 w-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
                <Bell className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2 text-2xl font-bold font-mono text-zinc-100">
              4 Active
            </div>
            <p className="mt-1 text-xs text-zinc-500">7-Day, 2-Day, Expiry & Failures</p>
          </div>
        </div>

        {/* SECTION 1: BATCH RECURRING PAYMENT RUNNER */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 space-y-5 shadow-sm">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-base">Recurring Batch Payment Runner</h3>
                <span className="px-2 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-300 font-mono uppercase">
                  Idempotent cron
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-1">
                Executes automated charges for all members whose active subscriptions have reached or passed their <code className="text-zinc-200">next_billing_date</code>.
              </p>
            </div>

            <Button
              onClick={handleRunBatch}
              disabled={processDuePayments.isPending}
              className="gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold shadow-md shadow-emerald-600/20"
            >
              <Play className="h-4 w-4 fill-white" />
              {processDuePayments.isPending ? "Executing Due Payments..." : "Process Due Payments Now"}
            </Button>
          </div>

          {/* Last batch execution report */}
          {lastBatchResult && (
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/20 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Batch Execution Result</span>
                </div>
                <span className="text-[11px] font-mono text-zinc-400">
                  Total Collected: {formatINR(lastBatchResult.total_collected)}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-2.5 rounded bg-zinc-900/80 border border-zinc-800">
                  <span className="text-[11px] text-zinc-400">Processed</span>
                  <p className="text-lg font-bold font-mono text-white">{lastBatchResult.processed}</p>
                </div>
                <div className="p-2.5 rounded bg-zinc-900/80 border border-zinc-800">
                  <span className="text-[11px] text-emerald-400">Succeeded</span>
                  <p className="text-lg font-bold font-mono text-emerald-400">{lastBatchResult.succeeded}</p>
                </div>
                <div className="p-2.5 rounded bg-zinc-900/80 border border-zinc-800">
                  <span className="text-[11px] text-red-400">Failed</span>
                  <p className="text-lg font-bold font-mono text-red-400">{lastBatchResult.failed}</p>
                </div>
              </div>

              {lastBatchResult.details?.length > 0 && (
                <div className="mt-2 space-y-1">
                  <p className="text-[11px] font-medium text-zinc-400">Processed Transactions:</p>
                  <div className="max-h-32 overflow-y-auto space-y-1 text-xs">
                    {lastBatchResult.details.map((d, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between px-3 py-1.5 rounded bg-zinc-900 border border-zinc-800 text-[11px]"
                      >
                        <span className="text-zinc-200">{d.member_name}</span>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-zinc-300">{formatINR(d.amount)}</span>
                          <Badge
                            variant={d.status === "succeeded" ? "success" : "destructive"}
                            className="text-[10px] py-0"
                          >
                            {d.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* SECTION 2: AUTOMATED RULES CONFIGURATION */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div>
              <h3 className="font-bold text-white text-base">Configured Automation Rules</h3>
              <p className="text-xs text-zinc-400 mt-0.5">Active triggers for multi-channel churn prevention & renewal nudges</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(statusData?.rules || []).map((rule) => (
              <div
                key={rule.id}
                className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-4 space-y-2 hover:border-zinc-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-zinc-200 text-xs">{rule.name}</span>
                  <Badge variant="outline" className="text-[10px] border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                    Active
                  </Badge>
                </div>
                <div className="space-y-1 text-xs text-zinc-400">
                  <div className="flex items-start gap-1.5">
                    <Clock className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                    <span><strong className="text-zinc-300">Trigger:</strong> {rule.trigger}</span>
                  </div>
                  <div className="flex items-start gap-1.5">
                    <Zap className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span><strong className="text-zinc-300">Action:</strong> {rule.action}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SECTION 3: AUDITED PAYMENT REMINDER NOTIFICATIONS */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 overflow-hidden shadow-sm">
          <div className="p-5 border-b border-zinc-800 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-base">Payment Reminders & Notification Audit Trail</h3>
              <p className="text-xs text-zinc-400 mt-0.5">Real-time log of automated SMS, WhatsApp, and in-app member dispatches</p>
            </div>
            <Badge variant="secondary" className="font-mono text-xs">
              {remindersData?.length || 0} Logged
            </Badge>
          </div>

          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800 bg-zinc-900/90">
                <TableHead>Recipient Member</TableHead>
                <TableHead>Notification Type</TableHead>
                <TableHead>Channel</TableHead>
                <TableHead>Message Content</TableHead>
                <TableHead>Sent Timestamp</TableHead>
                <TableHead>Delivery Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isRemindersLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12 text-zinc-500">
                    Loading notifications...
                  </TableCell>
                </TableRow>
              ) : !remindersData || remindersData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12 text-zinc-500">
                    No automated reminders dispatched yet. Click "Run Reminder Rule Evaluation" to check due dates.
                  </TableCell>
                </TableRow>
              ) : (
                remindersData.map((reminder) => (
                  <TableRow key={reminder.id} className="border-zinc-800/60">
                    <TableCell className="font-medium text-white">
                      <span className="font-semibold text-zinc-200">{reminder.member_name || "Member"}</span>
                    </TableCell>

                    <TableCell>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                        {reminder.reminder_type}
                      </span>
                    </TableCell>

                    <TableCell>
                      <div className="flex items-center gap-1.5 text-xs text-zinc-300">
                        {reminder.channel === "sms" ? (
                          <MessageSquare className="h-3.5 w-3.5 text-amber-400" />
                        ) : (
                          <Mail className="h-3.5 w-3.5 text-indigo-400" />
                        )}
                        <span className="uppercase text-[10px] font-mono font-semibold">{reminder.channel}</span>
                      </div>
                    </TableCell>

                    <TableCell className="text-xs text-zinc-400 max-w-xs truncate" title={reminder.message}>
                      {reminder.message}
                    </TableCell>

                    <TableCell className="text-xs text-zinc-400 font-mono">
                      {formatDate(reminder.created_at)}
                    </TableCell>

                    <TableCell>
                      <Badge variant="success" className="capitalize text-[10px]">
                        {reminder.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </main>
    </div>
  );
}
