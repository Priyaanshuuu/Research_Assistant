"use client";

import {
  useState,
  useEffect,
  useRef,
  useCallback,
  KeyboardEvent,
} from "react";
import { Bot, User, Send, Loader2, MessageSquare, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { sendChatMessage, fetchChatHistory } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

// ── Message bubble ────────────────────────────────────────────────────────────

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center
          justify-center mt-0.5
          ${isUser ? "bg-slate-900" : "bg-violet-100"}`}
      >
        {isUser ? (
          <User className="w-3.5 h-3.5 text-white" />
        ) : (
          <Bot className="w-3.5 h-3.5 text-violet-600" />
        )}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed
          ${isUser
            ? "bg-slate-900 text-white rounded-tr-sm"
            : "bg-slate-100 text-slate-800 rounded-tl-sm"
          }`}
      >
        {message.content}
      </div>
    </div>
  );
}

// ── Typing indicator ──────────────────────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex-shrink-0 w-7 h-7 rounded-full bg-violet-100 flex
                      items-center justify-center mt-0.5">
        <Bot className="w-3.5 h-3.5 text-violet-600" />
      </div>
      <div className="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex gap-1 items-center h-5">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Suggested questions ───────────────────────────────────────────────────────

const SUGGESTED: string[] = [
  "What were the most important findings?",
  "What are the main challenges in this area?",
  "What does the future outlook look like?",
  "Can you summarise the key applications?",
];

// ── Main component ────────────────────────────────────────────────────────────

interface ChatInterfaceProps {
  sessionId: string;
  topic: string;
}

export function ChatInterface({ sessionId, topic }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ── Load existing history on mount ────────────────────────────────────────
  useEffect(() => {
    const load = async () => {
      try {
        const history = await fetchChatHistory(sessionId);
        setMessages(history);
      } catch (err) {
        console.error("[ChatInterface] Failed to load history:", err);
      } finally {
        setHistoryLoading(false);
      }
    };
    load();
  }, [sessionId]);

  // ── Auto-scroll to latest message ─────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // ── Send ──────────────────────────────────────────────────────────────────
  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || loading) return;

      setInput("");
      setError(null);
      setLoading(true);

      // Optimistic user message
      const optimisticUser: ChatMessage = {
        id: `optimistic-${Date.now()}`,
        session_id: sessionId,
        role: "user",
        content: trimmed,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, optimisticUser]);

      try {
        const { user_message, assistant_message } = await sendChatMessage(
          sessionId,
          trimmed
        );

        // Replace optimistic message with real one from server
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== optimisticUser.id),
          user_message,
          assistant_message,
        ]);
      } catch (err: unknown) {
        setMessages((prev) =>
          prev.filter((m) => m.id !== optimisticUser.id)
        );
        const msg =
          err instanceof Error ? err.message : "Failed to send message.";
        setError(msg);
        setInput(trimmed); // restore input so user doesn't lose their question
      } finally {
        setLoading(false);
        textareaRef.current?.focus();
      }
    },
    [sessionId, loading]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send(input);
      }
    },
    [input, send]
  );

  const isEmpty = messages.length === 0 && !historyLoading;

  return (
    <div className="flex flex-col h-full bg-white border border-slate-200 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200 bg-slate-50">
        <MessageSquare className="w-4 h-4 text-violet-600" />
        <div>
          <p className="text-sm font-semibold text-slate-900">Ask the Research</p>
          <p className="text-xs text-slate-400 truncate max-w-[220px]">{topic}</p>
        </div>
      </div>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0">
        {/* Loading history */}
        {historyLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
          </div>
        )}

        {/* Empty state */}
        {isEmpty && (
          <div className="space-y-4">
            <div className="text-center py-4 space-y-2">
              <div className="w-10 h-10 rounded-full bg-violet-100 flex
                              items-center justify-center mx-auto">
                <Bot className="w-5 h-5 text-violet-600" />
              </div>
              <p className="text-sm font-medium text-slate-700">
                Ask anything about this research
              </p>
              <p className="text-xs text-slate-400">
                I have access to all the sources used in this report
              </p>
            </div>

            {/* Suggested questions */}
            <div className="space-y-2">
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => send(q)}
                  disabled={loading}
                  className="w-full text-left text-xs text-slate-600 bg-slate-50
                             hover:bg-slate-100 border border-slate-200 rounded-lg
                             px-3 py-2 transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Typing indicator */}
        {loading && <TypingIndicator />}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 text-xs text-red-600 bg-red-50
                          border border-red-200 rounded-lg px-3 py-2">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-slate-200 bg-white">
        <div className="flex gap-2 items-end">
          <Textarea
            ref={textareaRef}
            rows={1}
            placeholder="Ask a follow-up question… (Enter to send)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            className="resize-none text-sm min-h-[38px] max-h-[120px]
                       overflow-y-auto flex-1"
          />
          <Button
            type="button"
            size="sm"
            disabled={loading || !input.trim()}
            onClick={() => send(input)}
            className="flex-shrink-0 h-[38px] w-[38px] p-0"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-slate-400 mt-1.5">
          Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}