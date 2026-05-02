// REPLACE THIS FILE — shows authenticated user info using the server-side session

import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();

  // Fallback guard (middleware handles this, but belt-and-suspenders)
  if (!session?.user) redirect("/login");

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-2xl mx-auto space-y-4">
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-2">
          <p className="text-sm text-slate-500">Signed in as</p>
          <p className="font-semibold text-slate-900">{session.user.email}</p>
          {session.user.name && (
            <p className="text-slate-600">{session.user.name}</p>
          )}
          <p className="text-xs text-slate-400 font-mono break-all pt-2">
            JWT: {session.accessToken?.slice(0, 40)}…
          </p>
        </div>
        <p className="text-slate-400 text-sm">Day 2 — Auth ✓</p>
      </div>
    </main>
  );
}