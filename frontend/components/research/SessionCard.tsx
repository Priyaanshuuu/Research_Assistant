"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Trash2, Loader2 } from "lucide-react";
import { formatDistanceToNow } from "@/lib/date-utils";
import { deleteSession } from "@/lib/api";
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

const STATUS_DOT: Record<ResearchStatus, string> = {
  pending:      "bg-slate-400",
  searching:    "bg-blue-500 animate-pulse",
  evaluating:   "bg-yellow-500 animate-pulse",
  synthesizing: "bg-violet-500 animate-pulse",
  writing:      "bg-indigo-500 animate-pulse",
  completed:    "bg-green-500",
  failed:       "bg-red-500",
};

interface SessionCardProps {
  session: ResearchSession;
}

export function SessionCard({ session }: SessionCardProps) {
  const router = useRouter();
  const [deleting, setDeleting] = useState(false);
  const isClickable =
    session.status === "completed" || session.status === "failed";

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!confirm("Delete this research session? This cannot be undone.")) return;

    setDeleting(true);
    const toastId = toast.loading("Deleting session…");

    try {
      await deleteSession(session.id);
      toast.success("Session deleted.", { id: toastId });
      router.refresh();
    } catch {
      toast.error("Failed to delete session.", { id: toastId });
      setDeleting(false);
    }
  };

  const content = (
    <div
      className={`group bg-white border border-slate-200 rounded-xl p-5 space-y-3
        transition-all duration-150 hover:shadow-sm hover:border-slate-300 relative
        ${isClickable ? "cursor-pointer" : "cursor-default"}
        ${deleting ? "opacity-50 pointer-events-none" : ""}`}
    >
      <button
        type="button"
        onClick={handleDelete}
        disabled={deleting}
        className="absolute top-3 right-3 opacity-0 group-hover:opacity-100
                   transition-opacity p-1.5 rounded-lg hover:bg-red-50
                   text-slate-400 hover:text-red-500"
        title="Delete session"
      >
        {deleting ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <Trash2 className="w-3.5 h-3.5" />
        )}
      </button>
      <div className="flex items-center justify-between pr-6">
        <span
          className={`inline-flex items-center gap-1.5 text-xs font-medium
            px-2.5 py-0.5 rounded-full capitalize ${STATUS_COLOR[session.status]}`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT[session.status]}`}
          />
          {session.status}
        </span>
        <span className="text-xs text-slate-400">
          {formatDistanceToNow(session.created_at)}
        </span>
      </div>

      <p className="text-sm font-medium text-slate-900 line-clamp-2 pr-2">
        {session.topic}
      </p>

      {session.report_json?.title && (
        <p className="text-xs text-slate-500 line-clamp-1 italic">
          {session.report_json.title}
        </p>
      )}
      {session.error_message && (
        <p className="text-xs text-red-500 line-clamp-1">
          {session.error_message}
        </p>
      )}
    </div>
  );

  if (isClickable) {
    return (
      <Link href={`/research/${session.id}`} className="block">
        {content}
      </Link>
    );
  }
  return content;
}