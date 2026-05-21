"use client";

import Link from "next/link";
import { formatDistanceToNow } from "../../lib/data-utils"
import { Badge } from "@/components/ui/badge";
import type { ResearchSession, ResearchStatus } from "@/lib/types";

const STATUS_COLOR: Record<ResearchStatus, string> = {
  pending:      "bg-slate-100 text-slate-600",
  searching:    "bg-blue-100 text-blue-700",
  evaluating:   "bg-yellow-100 text-yellow-700",
  synthesizing: "bg-violet-100 text-violet-700",
  writing:      "bg-indigo-100 text-indigo-700",
  completed:    "bg-green-100 text-green-700",
  failed:       "bg-red-100 text-red-700",
};

interface SessionCardProps {
  session: ResearchSession;
}

export function SessionCard({ session }: SessionCardProps) {
  const isClickable = session.status === "completed" || session.status === "failed";

  const content = (
    <div
      className={`bg-white border border-slate-200 rounded-xl p-5 space-y-3
        transition-shadow hover:shadow-sm
        ${isClickable ? "cursor-pointer" : "cursor-default opacity-80"}`}
    >
      {/* Status badge */}
      <div className="flex items-center justify-between">
        <span
          className={`text-xs font-medium px-2.5 py-0.5 rounded-full capitalize
            ${STATUS_COLOR[session.status]}`}
        >
          {session.status}
        </span>
        <span className="text-xs text-slate-400">
          {formatDistanceToNow(session.created_at)}
        </span>
      </div>

      {/* Topic */}
      <p className="text-sm font-medium text-slate-900 line-clamp-2">{session.topic}</p>

      {/* Report title if completed */}
      {session.report_json?.title && (
        <p className="text-xs text-slate-500 line-clamp-1">
          {session.report_json.title}
        </p>
      )}

      {/* Error */}
      {session.error_message && (
        <p className="text-xs text-red-500 line-clamp-1">{session.error_message}</p>
      )}
    </div>
  );

  if (isClickable) {
    return <Link href={`/research/${session.id}`}>{content}</Link>;
  }
  return content;
}