// REPLACE THIS FILE — passes sessionId to ReportViewer, adds error state polish

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
if (!authSession?.user || !authSession.accessToken) redirect("/login");

const researchSession = await getSession(params.id, authSession.accessToken);

  if (!researchSession) {
    return (
      <AppLayout>
        <div className="max-w-2xl mx-auto text-center py-24 space-y-4">
          <div className="w-14 h-14 rounded-full bg-red-100 flex items-center
                          justify-center mx-auto">
            <span className="text-2xl">🔍</span>
          </div>
          <p className="text-lg font-semibold text-slate-900">Session not found</p>
          <p className="text-sm text-slate-500">
            This session doesn&apos;t exist or you don&apos;t have access to it.
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
        <div className="space-y-1">
          <p className="text-xs text-slate-400 uppercase tracking-wide font-medium">
            Research Topic
          </p>
          <h1 className="text-xl font-bold text-slate-900 leading-snug">
            {researchSession.topic}
          </h1>
        </div>
        {isRunning && (
          <div className="max-w-md">
            <AgentProgressBoard
              sessionId={researchSession.id}
              initialStatus={researchSession.status}
            />
          </div>
        )}
        {isFailed && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">⚠️</span>
              <p className="font-semibold text-red-800">Research Failed</p>
            </div>
            <p className="text-sm text-red-700">
              {researchSession.error_message ?? "An unknown error occurred."}
            </p>
            <a
              href="/research/new"
              className="inline-block text-sm font-medium text-red-700
                         underline hover:no-underline"
            >
              Try again with a new topic →
            </a>
          </div>
        )}
        {isCompleted && researchSession.report_json && (
          <div className="flex flex-col lg:flex-row gap-6 items-start">
            <div className="w-full lg:w-[60%]">
              <ReportViewer
                report={researchSession.report_json}
                sessionId={researchSession.id}
              />
            </div>
            <div
              className="w-full lg:w-[40%] lg:sticky lg:top-20
                         lg:h-[calc(100vh-6rem)]"
            >
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