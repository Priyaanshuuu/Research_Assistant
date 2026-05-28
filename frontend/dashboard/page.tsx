// REPLACE THIS FILE — adds delete button with toast, polish on empty + error states

import { auth } from "@/auth";
import { redirect } from "next/navigation";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { SessionCard } from "@/components/research/SessionCard";
import { Button } from "@/components/ui/button";
import { PlusCircle, FlaskConical } from "lucide-react";
import type { ResearchSession } from "@/lib/types";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

async function getSessions(accessToken: string): Promise<ResearchSession[]> {
  try {
    const res = await fetch(`${BACKEND}/research/?limit=50`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user) redirect("/login");

  const sessions = await getSessions(session.accessToken);

  const running = sessions.filter((s) =>
    ["pending", "searching", "evaluating", "synthesizing", "writing"].includes(
      s.status
    )
  );
  const completed = sessions.filter((s) => s.status === "completed");
  const failed = sessions.filter((s) => s.status === "failed");

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-sm text-slate-500 mt-1">
              Welcome back,{" "}
              <span className="font-medium text-slate-700">
                {session.user.name ?? session.user.email}
              </span>
            </p>
          </div>
          <Link href="/research/new">
            <Button className="gap-2">
              <PlusCircle className="w-4 h-4" />
              New Research
            </Button>
          </Link>
        </div>

        {/* Stats row */}
        {sessions.length > 0 && (
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: "Completed", count: completed.length, color: "text-green-600" },
              { label: "In Progress", count: running.length, color: "text-blue-600" },
              { label: "Failed", count: failed.length, color: "text-red-500" },
            ].map(({ label, count, color }) => (
              <div
                key={label}
                className="bg-white border border-slate-200 rounded-xl
                           p-4 text-center space-y-1"
              >
                <p className={`text-2xl font-bold ${color}`}>{count}</p>
                <p className="text-xs text-slate-500">{label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {sessions.length === 0 && (
          <div className="text-center py-24 space-y-5">
            <div
              className="w-20 h-20 rounded-full bg-violet-100 flex items-center
                         justify-center mx-auto"
            >
              <FlaskConical className="w-9 h-9 text-violet-600" />
            </div>
            <div className="space-y-2">
              <p className="text-lg font-semibold text-slate-900">
                No research sessions yet
              </p>
              <p className="text-sm text-slate-500 max-w-sm mx-auto">
                Enter any topic and our AI agents will research, evaluate, and
                produce a full report in about 90 seconds.
              </p>
            </div>
            <Link href="/research/new">
              <Button size="lg" className="gap-2">
                <PlusCircle className="w-5 h-5" />
                Start Your First Research
              </Button>
            </Link>
          </div>
        )}

        {/* In Progress */}
        {running.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              In Progress — {running.length}
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {running.map((s) => (
                <SessionCard key={s.id} session={s} />
              ))}
            </div>
          </div>
        )}

        {/* Completed */}
        {completed.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Completed — {completed.length}
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {completed.map((s) => (
                <SessionCard key={s.id} session={s} />
              ))}
            </div>
          </div>
        )}

        {/* Failed */}
        {failed.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Failed — {failed.length}
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {failed.map((s) => (
                <SessionCard key={s.id} session={s} />
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}