"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { startResearch } from "@/lib/api";
import { FlaskConical, Loader2 } from "lucide-react";

const EXAMPLE_TOPICS = [
  "The impact of large language models on software engineering productivity",
  "How transformer architecture changed modern AI research",
  "The role of quantum computing in breaking current encryption standards",
  "Advances in CRISPR gene editing for treating genetic diseases",
];

export function ResearchForm() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = topic.trim();
      if (trimmed.length < 10) {
        setError("Please enter a topic of at least 10 characters.");
        return;
      }

      setError(null);
      setLoading(true);

      try {
        const { session_id } = await startResearch(trimmed);
        router.push(`/research/${session_id}`);
      } catch (err: unknown) {
        const msg =
          err instanceof Error ? err.message : "Failed to start research. Please try again.";
        setError(msg);
        setLoading(false);
      }
    },
    [topic, router]
  );

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label
            htmlFor="topic"
            className="block text-sm font-medium text-slate-700"
          >
            Research topic
          </label>
          <Textarea
            id="topic"
            rows={3}
            placeholder="e.g. The impact of large language models on software engineering productivity..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
            className="resize-none text-sm"
            maxLength={500}
          />
          <div className="flex justify-between items-center">
            {error && <p className="text-xs text-red-500">{error}</p>}
            <p className="text-xs text-slate-400 ml-auto">{topic.length}/500</p>
          </div>
        </div>

        <Button
          type="submit"
          disabled={loading || topic.trim().length < 10}
          className="w-full gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Starting research…
            </>
          ) : (
            <>
              <FlaskConical className="w-4 h-4" />
              Start Research
            </>
          )}
        </Button>
      </form>

      {/* Example topics */}
      <div className="space-y-2">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
          Example topics
        </p>
        <div className="space-y-2">
          {EXAMPLE_TOPICS.map((t) => (
            <button
              key={t}
              type="button"
              disabled={loading}
              onClick={() => setTopic(t)}
              className="w-full text-left text-xs text-slate-600 bg-slate-50 hover:bg-slate-100
                         border border-slate-200 rounded-lg px-3 py-2 transition-colors
                         disabled:opacity-50"
            >
              {t}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}