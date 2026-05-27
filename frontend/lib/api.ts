// REPLACE THIS FILE — adds chat history fetch helper

import axios from "axios";
import { getSession } from "next-auth/react";
import type { ResearchSession, ChatMessage, ResearchStatus } from "@/lib/types";

// ── Axios instance ────────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: "/api/backend",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use(async (config) => {
  try {
    const session = await getSession();
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`;
    }
  } catch (err) {
    console.error("[api] Failed to attach token:", err);
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      console.warn("[api] 401 — token may have expired");
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Types ─────────────────────────────────────────────────────────────────────

export interface StartResearchResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface StatusResponse {
  session_id: string;
  status: ResearchStatus;
  progress_pct: number;
  latest_event: string | null;
  error_message: string | null;
}

// ── Research helpers ──────────────────────────────────────────────────────────

export async function startResearch(topic: string): Promise<StartResearchResponse> {
  const { data } = await api.post<StartResearchResponse>("/research/start", { topic });
  return data;
}

export async function fetchStatus(sessionId: string): Promise<StatusResponse> {
  const { data } = await api.get<StatusResponse>(`/research/status/${sessionId}`);
  return data;
}

export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  const { data } = await api.get<ResearchSession>(`/research/${sessionId}`);
  return data;
}

export async function fetchSessions(): Promise<ResearchSession[]> {
  const { data } = await api.get<ResearchSession[]>("/research/");
  return data;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await api.delete(`/research/${sessionId}`);
}

// ── Chat helpers ──────────────────────────────────────────────────────────────

export async function sendChatMessage(
  sessionId: string,
  message: string
): Promise<{ user_message: ChatMessage; assistant_message: ChatMessage }> {
  const { data } = await api.post("/chat/", {
    session_id: sessionId,
    message,
  });
  return data;
}

export async function fetchChatHistory(sessionId: string): Promise<ChatMessage[]> {
  const { data } = await api.get<ChatMessage[]>(`/chat/history/${sessionId}`);
  return data;
}