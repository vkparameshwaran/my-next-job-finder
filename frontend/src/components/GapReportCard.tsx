import clsx from "clsx";
import type { GapReport } from "../types";

interface Props {
  report: GapReport;
}

export default function GapReportCard({ report }: Props) {
  const overlapEntries = Object.entries(report.keyword_overlap);
  const hits = overlapEntries.filter(([, hit]) => hit).length;

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <div className="md:col-span-1 bg-white rounded-lg border border-slate-200 p-5">
        <p className="text-xs uppercase tracking-wide text-slate-500">ATS Score</p>
        <p className="text-5xl font-bold text-slate-900 mt-2">{report.ats_score}</p>
        <p className="text-xs text-slate-500 mt-1">out of 100</p>
      </div>

      <div className="md:col-span-2 bg-white rounded-lg border border-slate-200 p-5">
        <p className="text-sm font-medium text-slate-900 mb-2">High-level issues</p>
        {report.issues.length === 0 ? (
          <p className="text-sm text-slate-500">No high-level issues found.</p>
        ) : (
          <ul className="space-y-2">
            {report.issues.map((issue, i) => (
              <li
                key={i}
                className={clsx(
                  "text-sm p-2 rounded border-l-4",
                  issue.severity === "error" && "bg-red-50 border-red-500 text-red-900",
                  issue.severity === "warning" &&
                    "bg-amber-50 border-amber-500 text-amber-900",
                  issue.severity === "info" && "bg-blue-50 border-blue-500 text-blue-900",
                )}
              >
                <span className="font-medium">{issue.kind}:</span> {issue.message}
              </li>
            ))}
          </ul>
        )}
      </div>

      {overlapEntries.length > 0 && (
        <div className="md:col-span-3 bg-white rounded-lg border border-slate-200 p-5">
          <p className="text-sm font-medium text-slate-900 mb-2">
            Keyword overlap with role description ({hits}/{overlapEntries.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {overlapEntries.map(([word, hit]) => (
              <span
                key={word}
                className={clsx(
                  "text-xs px-2 py-0.5 rounded",
                  hit ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-500",
                )}
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
