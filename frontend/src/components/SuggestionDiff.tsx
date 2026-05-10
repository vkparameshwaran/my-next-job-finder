import clsx from "clsx";
import type { Bullet, Suggestion } from "../types";

interface Props {
  bullet: Bullet;
  suggestion: Suggestion;
  onToggle: (id: string, accepted: boolean | null) => void;
}

export default function SuggestionDiff({ bullet, suggestion, onToggle }: Props) {
  const state = suggestion.accepted;

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {suggestion.issue}
        </span>
        <span className="text-xs text-slate-400">{suggestion.rationale}</span>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <div
          className={clsx(
            "p-3 rounded text-sm border",
            state === false
              ? "bg-slate-50 border-slate-300"
              : "bg-red-50 border-red-200 text-red-900 line-through",
          )}
        >
          <p className="text-xs font-medium uppercase mb-1 not-italic no-underline text-slate-500">
            Original
          </p>
          {bullet.text}
        </div>
        <div
          className={clsx(
            "p-3 rounded text-sm border",
            state === true
              ? "bg-green-50 border-green-300 text-green-900"
              : "bg-slate-50 border-slate-300",
          )}
        >
          <p className="text-xs font-medium uppercase mb-1 text-slate-500">
            Suggested rewrite
          </p>
          {suggestion.rewrite}
        </div>
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => onToggle(suggestion.id, state === true ? null : true)}
          className={clsx(
            "px-3 py-1.5 rounded text-sm font-medium transition",
            state === true
              ? "bg-green-600 text-white"
              : "bg-slate-100 text-slate-700 hover:bg-slate-200",
          )}
        >
          {state === true ? "Accepted" : "Accept"}
        </button>
        <button
          type="button"
          onClick={() => onToggle(suggestion.id, state === false ? null : false)}
          className={clsx(
            "px-3 py-1.5 rounded text-sm font-medium transition",
            state === false
              ? "bg-slate-700 text-white"
              : "bg-slate-100 text-slate-700 hover:bg-slate-200",
          )}
        >
          {state === false ? "Rejected" : "Reject"}
        </button>
      </div>
    </div>
  );
}
