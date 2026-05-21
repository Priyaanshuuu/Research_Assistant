
import { auth } from "@/auth";
import { redirect } from "next/navigation";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { SessionCard } from "@/components/research/SessionCard";
import { Button } from "@/components/ui/button";
import { PlusCircle } from "lucide-react";
import type { ResearchSession } from "@/lib/types";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

async function getSessions(accessToken: string): Promise<ResearchSession[]> {
  try {
    const res = await fetch(`${BACKEND}/research/?limit=20`, {
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
    ["pending", "searching", "evaluating", "synthesizing", "writing"].includes(s.status)
  );
  const completed = sessions.filter((s) => s.status === "completed");
  const failed = sessions.filter((s) => s.status === "failed");

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-sm text-slate-500 mt-1">
              Welcome back, {session.user.name ?? session.user.email}
            </p>
          </div>
          <Link href="/research/new">
            <Button className="gap-2">
              <PlusCircle className="w-4 h-4" />
              New Research
            </Button>
          </Link>
        </div>

        {/* Empty state */}
        {sessions.length === 0 && (
          <div className="text-center py-20 space-y-4">
            <div className="w-16 h-16 rounded-full bg-violet-100 flex items-center
                            justify-center mx-auto">
              <PlusCircle className="w-7 h-7 text-violet-600" />
            </div>
            <div className="space-y-1">
              <p className="font-medium text-slate-900">No research yet</p>
              <p className="text-sm text-slate-500">
                Start your first research session to see it here.
              </p>
            </div>
            <Link href="/research/new">
              <Button>Start Research</Button>
            </Link>
          </div>
        )}

        {/* Running sessions */}
        {running.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">
              In Progress ({running.length})
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {running.map((s) => (
                <SessionCard key={s.id} session={s} />
              ))}
            </div>
          </div>
        )}

        {/* Completed sessions */}
        {completed.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">
              Completed ({completed.length})
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {completed.map((s) => (
                <SessionCard key={s.id} session={s} />
              ))}
            </div>
          </div>
        )}

        {/* Failed sessions */}
        {failed.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">
              Failed ({failed.length})
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