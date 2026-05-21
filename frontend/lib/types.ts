// REPLACE THIS FILE — extends Day 2 types with report and agent event shapes

export type ResearchStatus =
  | "pending"
  | "searching"
  | "evaluating"
  | "synthesizing"
  | "writing"
  | "completed"
  | "failed";

export interface User {
  id: string;
  email: string;
  name: string | null;
  provider: "email" | "google";
  createdAt: string;
}

export interface AgentEvent {
  id: string;
  session_id: string;
  agent_name: string;
  event_type: string;
  payload: Record<string, unknown> | null;
  created_at: string;
}

export interface ReportSection {
  heading: string;
  body: string;
  citations: string[];
}

export interface ResearchReport {
  title: string;
  summary: string;
  sections: ReportSection[];
  key_takeaways: string[];
  all_citations: string[];
  topic: string;
  generated_at: string;
}

export interface ResearchSession {
  id: string;
  user_id: string;
  topic: string;
  status: ResearchStatus;
  report_json: ResearchReport | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  agent_events: AgentEvent[];
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}