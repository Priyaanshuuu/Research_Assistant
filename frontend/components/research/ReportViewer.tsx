"use client";

import { useState } from "react";
import { ExternalLink, ChevronDown, ChevronUp, Lightbulb, BookOpen } from "lucide-react";
import { formatDate } from "@/lib/date-utils";
import type { ResearchReport } from "@/lib/types";

// ── Citation link ─────────────────────────────────────────────────────────────

function CitationLink({ url, index }: { url: string; index: number }) {
  let hostname = url;
  try {
    hostname = new URL(url).hostname.replace("www.", "");
  } catch {}

  return (
    
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 text-xs text-violet-600 hover:text-violet-800
                 bg-violet-50 hover:bg-violet-100 border border-violet-200 rounded px-1.5 py-0.5
                 transition-colors"
    >
      [{index}] {hostname}
      <ExternalLink className="w-2.5 h-2.5" />
    </a>
  );
}

// ── Section ───────────────────────────────────────────────────────────────────

function ReportSection({
  section,
  index,
  allCitations,
}: {
  section: { heading: string; body: string; citations: string[] };
  index: number;
  allCitations: string[];
}) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      {/* Section header */}
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-4
                   bg-slate-50 hover:bg-slate-100 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-100 text-violet-700
                           text-xs font-semibold flex items-center justify-center">
            {index}
          </span>
          <h3 className="text-sm font-semibold text-slate-900">{section.heading}</h3>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
        )}
      </button>

      {/* Section body */}
      {expanded && (
        <div className="px-5 py-4 space-y-4 bg-white">
          <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
            {section.body}
          </p>

          {/* Inline citations */}
          {section.citations.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {section.citations.map((url) => {
                const idx = allCitations.indexOf(url) + 1;
                return <CitationLink key={url} url={url} index={idx || 0} />;
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

interface ReportViewerProps {
  report: ResearchReport;
}

export function ReportViewer({ report }: ReportViewerProps) {
  const [showAllCitations, setShowAllCitations] = useState(false);
  const visibleCitations = showAllCitations
    ? report.all_citations
    : report.all_citations.slice(0, 6);

  return (
    <div className="space-y-8">
      {/* Report header */}
      <div className="space-y-3">
        <h1 className="text-2xl font-bold text-slate-900">{report.title}</h1>
        <p className="text-xs text-slate-400">
          Generated {formatDate(report.generated_at)}
        </p>

        {/* Summary */}
        <div className="bg-violet-50 border border-violet-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="w-4 h-4 text-violet-600" />
            <span className="text-sm font-semibold text-violet-800">
              Executive Summary
            </span>
          </div>
          <p className="text-sm text-violet-900 leading-relaxed">{report.summary}</p>
        </div>
      </div>

      {/* Key takeaways */}
      {report.key_takeaways?.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-amber-600" />
            <span className="text-sm font-semibold text-amber-800">Key Takeaways</span>
          </div>
          <ul className="space-y-2">
            {report.key_takeaways.map((t, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-amber-900">
                <span className="flex-shrink-0 text-amber-500 font-bold mt-0.5">
                  {i + 1}.
                </span>
                {t}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Sections */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-slate-900">Report Sections</h2>
        {report.sections.map((section, i) => (
          <ReportSection
            key={i}
            section={section}
            index={i + 1}
            allCitations={report.all_citations}
          />
        ))}
      </div>

      {/* All citations */}
      {report.all_citations.length > 0 && (
        <div className="border border-slate-200 rounded-xl p-5 space-y-3">
          <h2 className="text-sm font-semibold text-slate-900">
            All Citations ({report.all_citations.length})
          </h2>
          <ol className="space-y-1.5">
            {visibleCitations.map((url, i) => (
              <li key={url} className="flex items-start gap-2">
                <span className="text-xs text-slate-400 mt-0.5 w-5 flex-shrink-0">
                  {i + 1}.
                </span>
                
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-violet-600 hover:underline break-all"
                >
                  {url}
                </a>
              </li>
            ))}
          </ol>

          {report.all_citations.length > 6 && (
            <button
              type="button"
              onClick={() => setShowAllCitations((v) => !v)}
              className="text-xs text-slate-500 hover:text-slate-700 transition-colors"
            >
              {showAllCitations
                ? "Show fewer"
                : `Show ${report.all_citations.length - 6} more…`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}