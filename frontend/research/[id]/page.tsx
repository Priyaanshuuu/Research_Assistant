// REPLACE THIS FILE — adds ChatInterface panel next to report

import { auth } from "@/auth";
import { redirect } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import { AgentProgressBoard } from "@/components/research/AgentProgressBoard";
import { ReportViewer } from "@/components/research/ReportViewer";
import { ChatInterface } from "@/components/chat/ChatInterface";
import type { ResearchSession } from "@/lib/types";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

async function getSession(
  sessionId: string,
  accessToken: string
): Promise<ResearchSession | null> {
  try {
    const res = await fetch(`${BACKEND}/research/${sessionId}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function ResearchSessionPage({
  params,
}: {
  params: { id: string };
}) {
  const authSession = await auth();
  if (!authSession?.user) redirect("/login");

  const researchSession = await getSession(params.id, authSession.accessToken);

  if (!researchSession) {
    return (
      <AppLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <p className="text-slate-500">
            Session not found or you don&apos;t have access.
          </p>
        </div>
      </AppLayout>
    );
  }

  const isCompleted = researchSession.status === "completed";
  const isFailed = researchSession.status === "failed";
  const isRunning = !isCompleted && !isFailed;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Topic heading */}
        <div className="space-y-1">
          <p className="text-xs text-slate-400 uppercase tracking-wide font-medium">
            Research Topic
          </p>
          <h1 className="text-xl font-bold text-slate-900">
            {researchSession.topic}
          </h1>
        </div>

        {/* Running — show progress board centred */}
        {isRunning && (
          <div className="max-w-md">
            <AgentProgressBoard
              sessionId={researchSession.id}
              initialStatus={researchSession.status}
            />
          </div>
        )}

        {/* Failed */}
        {isFailed && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 space-y-2">
            <p className="font-semibold text-red-800">Research Failed</p>
            <p className="text-sm text-red-700">
              {researchSession.error_message ?? "An unknown error occurred."}
            </p>
          </div>
        )}

        {/* Completed — report + chat side by side */}
        {isCompleted && researchSession.report_json && (
          <div className="flex flex-col lg:flex-row gap-6 items-start">
            {/* Report — takes 60% on large screens */}
            <div className="w-full lg:w-[60%]">
              <ReportViewer report={researchSession.report_json} />
            </div>

            {/* Chat — sticky sidebar on large screens */}
            <div className="w-full lg:w-[40%] lg:sticky lg:top-20 lg:h-[calc(100vh-6rem)]">
              <ChatInterface
                sessionId={researchSession.id}
                topic={researchSession.topic}
              />
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}