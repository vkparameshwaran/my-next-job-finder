import { useMemo, useState } from "react";
import GapReportCard from "../components/GapReportCard";
import SuggestionDiff from "../components/SuggestionDiff";
import { exportResume } from "../api/client";
import type { AnalyzeResponse, Bullet, Suggestion } from "../types";

interface Props {
  analysis: AnalyzeResponse;
}

function collectBullets(resume: AnalyzeResponse["resume"]): Map<string, Bullet> {
  const map = new Map<string, Bullet>();
  for (const job of resume.experience) for (const b of job.bullets) map.set(b.id, b);
  for (const project of resume.projects) for (const b of project.bullets) map.set(b.id, b);
  for (const degree of resume.education) for (const b of degree.bullets) map.set(b.id, b);
  return map;
}

export default function Review({ analysis }: Props) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>(
    analysis.report.suggestions,
  );
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const bulletMap = useMemo(() => collectBullets(analysis.resume), [analysis.resume]);

  const onToggle = (id: string, accepted: boolean | null) => {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, accepted } : s)),
    );
  };

  const onExport = async () => {
    setExporting(true);
    setExportError(null);
    try {
      await exportResume(analysis.record_id, suggestions);
    } catch (err) {
      setExportError(err instanceof Error ? err.message : String(err));
    } finally {
      setExporting(false);
    }
  };

  const acceptedCount = suggestions.filter((s) => s.accepted === true).length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Review</h1>
        <p className="text-slate-600 mt-1">
          Accept the rewrites you like; reject the ones you don't. Then export.
        </p>
      </div>

      <GapReportCard report={analysis.report} />

      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-3">
          Bullet-level suggestions ({suggestions.length})
        </h2>
        {suggestions.length === 0 ? (
          <p className="text-sm text-slate-500">
            No bullet-level suggestions — the resume is already tight.
          </p>
        ) : (
          <div className="space-y-3">
            {suggestions.map((s) => {
              const bullet = bulletMap.get(s.bullet_id);
              if (!bullet) return null;
              return (
                <SuggestionDiff
                  key={s.id}
                  bullet={bullet}
                  suggestion={s}
                  onToggle={onToggle}
                />
              );
            })}
          </div>
        )}
      </div>

      {exportError && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-800">
          {exportError}
        </div>
      )}

      <div className="sticky bottom-4 bg-white border border-slate-200 rounded-lg p-4 flex items-center justify-between shadow-sm">
        <p className="text-sm text-slate-700">
          {acceptedCount} of {suggestions.length} suggestions accepted
        </p>
        <button
          type="button"
          onClick={onExport}
          disabled={exporting}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium px-4 py-2 rounded-md transition"
        >
          {exporting ? "Exporting…" : "Export resume"}
        </button>
      </div>
    </div>
  );
}

