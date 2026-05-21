"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Progress } from "@/components/ui/progress";
import { fetchStatus } from "@/lib/api";
import type { ResearchStatus } from "@/lib/types";
import {
  CheckCircle2,
  Circle,
  Loader2,
  XCircle,
  Brain,
  Search,
  Star,
  GitMerge,
  PenLine,
} from "lucide-react";

interface AgentNode {
  key: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  activeStatuses: ResearchStatus[];
  doneStatuses: ResearchStatus[];
}

const NODES: AgentNode[] = [
  {
    key: "planner",
    label: "Planner",
    description: "Decomposing topic into sub-questions",
    icon: <Brain className="w-4 h-4" />,
    activeStatuses: ["pending", "searching"],
    doneStatuses: ["evaluating", "synthesizing", "writing", "completed"],
  },
  {
    key: "searcher",
    label: "Searcher",
    description: "Searching the web for sources",
    icon: <Search className="w-4 h-4" />,
    activeStatuses: ["searching"],
    doneStatuses: ["evaluating", "synthesizing", "writing", "completed"],
  },
  {
    key: "evaluator",
    label: "Evaluator",
    description: "Scoring sources for credibility & relevance",
    icon: <Star className="w-4 h-4" />,
    activeStatuses: ["evaluating"],
    doneStatuses: ["synthesizing", "writing", "completed"],
  },
  {
    key: "synthesizer",
    label: "Synthesizer",
    description: "Merging findings into a narrative",
    icon: <GitMerge className="w-4 h-4" />,
    activeStatuses: ["synthesizing"],
    doneStatuses: ["writing", "completed"],
  },
  {
    key: "writer",
    label: "Writer",
    description: "Generating structured report",
    icon: <PenLine className="w-4 h-4" />,
    activeStatuses: ["writing"],
    doneStatuses: ["completed"],
  },
];

type NodeState = "idle" | "active" | "done" | "failed";

function getNodeState(node: AgentNode, status: ResearchStatus): NodeState {
  if (status === "failed") return "failed";
  if (node.doneStatuses.includes(status)) return "done";
  if (node.activeStatuses.includes(status)) return "active";
  return "idle";
}

function NodeIndicator({
  node,
  nodeState,
}: {
  node: AgentNode;
  nodeState: NodeState;
}) {
  const isActive = nodeState === "active";
  const isDone = nodeState === "done";
  const isFailed = nodeState === "failed";

  return (
    <div className="flex items-start gap-3">
      {/* Icon bubble */}
      <div
        className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center
          transition-all duration-500
          ${isDone ? "bg-green-100 text-green-600" : ""}
          ${isActive ? "bg-violet-100 text-violet-600 ring-2 ring-violet-300 ring-offset-1" : ""}
          ${isFailed ? "bg-red-100 text-red-500" : ""}
          ${nodeState === "idle" ? "bg-slate-100 text-slate-400" : ""}
        `}
      >
        {isDone && <CheckCircle2 className="w-4 h-4" />}
        {isActive && <Loader2 className="w-4 h-4 animate-spin" />}
        {isFailed && <XCircle className="w-4 h-4" />}
        {nodeState === "idle" && <Circle className="w-4 h-4" />}
      </div>
      <div className="pt-1 space-y-0.5">
        <p
          className={`text-sm font-medium transition-colors
            ${isDone ? "text-green-700" : ""}
            ${isActive ? "text-violet-700" : ""}
            ${isFailed ? "text-red-600" : ""}
            ${nodeState === "idle" ? "text-slate-400" : ""}
          `}
        >
          {node.label}
        </p>
        <p className="text-xs text-slate-400">{node.description}</p>
      </div>
    </div>
  );
}

interface AgentProgressBoardProps {
  sessionId: string;
  initialStatus: ResearchStatus;
}

export function AgentProgressBoard({
  sessionId,
  initialStatus,
}: AgentProgressBoardProps) {
  const router = useRouter();
  const [statusData, setStatusData] = useState<{
    status: ResearchStatus;
    progress_pct: number;
    latest_event: string | null;
    error_message: string | null;
  }>({
    status: initialStatus,
    progress_pct: 0,
    latest_event: null,
    error_message: null,
  });

  const poll = useCallback(async () => {
    try {
      const data = await fetchStatus(sessionId);
      setStatusData(data);

      if (data.status === "completed") {
        setTimeout(() => router.refresh(), 1200);
      }
    } catch (err) {
      console.error("[AgentProgressBoard] Poll error:", err);
    }
  }, [sessionId, router]);

  useEffect(() => {
    const TERMINAL = ["completed", "failed"];
    if (TERMINAL.includes(statusData.status)) return;

    // Delay initial poll to avoid cascading renders
    const timeout = setTimeout(() => poll(), 0);
    const interval = setInterval(poll, 3000);
    return () => {
      clearTimeout(timeout);
      clearInterval(interval);
    };
  }, [poll, statusData.status]);

  const { status, progress_pct, latest_event, error_message } = statusData;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">Agent Pipeline</h2>
          <span className="text-sm font-medium text-slate-500">{progress_pct}%</span>
        </div>
        <Progress value={progress_pct} className="h-1.5" />
        {latest_event && (
          <p className="text-xs text-slate-400 pt-1">{latest_event}</p>
        )}
      </div>
      <div className="space-y-4">
        {NODES.map((node) => (
          <NodeIndicator
            key={node.key}
            node={node}
            nodeState={getNodeState(node, status)}
          />
        ))}
      </div>
      {status === "failed" && error_message && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
          <p className="font-medium mb-1">Research failed</p>
          <p className="text-xs">{error_message}</p>
        </div>
      )}
    </div>
  );
}