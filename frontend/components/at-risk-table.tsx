import React from "react";
import Link from "next/link";
import { AlertCircle, ArrowRight, Clock, Phone, Mail, CreditCard } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AtRiskMemberItem } from "@/types/api";

interface AtRiskTableProps {
  items: AtRiskMemberItem[];
  isLoading?: boolean;
}

export function AtRiskTable({ items, isLoading }: AtRiskTableProps) {
  return (
    <Card className="border-zinc-800 bg-zinc-900/70">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-amber-400" />
            <CardTitle className="text-base font-semibold text-white">
              At-Risk Members Action Center
            </CardTitle>
            <Badge variant="warning" className="ml-1">
              {items.length} {items.length === 1 ? "member" : "members"} require attention
            </Badge>
          </div>
          <CardDescription className="text-xs text-zinc-400 mt-1">
            Members with active memberships expiring within 7 days or overdue failed payments
          </CardDescription>
        </div>
        <Link href="/memberships">
          <Button variant="outline" size="sm" className="h-8 gap-1 text-xs">
            Manage Memberships <ArrowRight className="h-3 w-3" />
          </Button>
        </Link>
      </CardHeader>

      <CardContent>
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center text-zinc-500">
            <div className="h-10 w-10 rounded-full bg-emerald-950/40 text-emerald-400 flex items-center justify-center mb-2">
              ✓
            </div>
            <p className="text-sm font-medium text-zinc-300">All memberships healthy!</p>
            <p className="text-xs text-zinc-500 mt-0.5">
              No members are currently expiring within 7 days or have overdue payments.
            </p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {items.map((item) => {
              const isPayment = item.risk_reason.toLowerCase().includes("failed payment");
              const isExpiring = item.days_remaining !== null && item.days_remaining !== undefined;

              return (
                <div
                  key={item.member_id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-lg border border-zinc-800/80 bg-zinc-900/90 p-3.5 transition-colors hover:border-zinc-700/80"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                        isPayment
                          ? "bg-red-950/60 text-red-400 border border-red-800/50"
                          : "bg-amber-950/60 text-amber-400 border border-amber-800/50"
                      }`}
                    >
                      {isPayment ? <CreditCard className="h-4 w-4" /> : <Clock className="h-4 w-4" />}
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-zinc-100">{item.name}</span>
                        <Badge variant={isPayment ? "destructive" : "warning"} className="text-[10px] py-0 px-2">
                          {item.risk_reason}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-4 text-xs text-zinc-400 mt-1">
                        <span className="flex items-center gap-1">
                          <Phone className="h-3 w-3 text-zinc-500" />
                          {item.phone}
                        </span>
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3 text-zinc-500" />
                          {item.email}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center">
                    <Link href="/memberships">
                      <Button size="sm" variant="secondary" className="h-7 text-xs bg-zinc-800 hover:bg-zinc-700">
                        {isPayment ? "Collect Payment" : "Renew Plan"}
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
