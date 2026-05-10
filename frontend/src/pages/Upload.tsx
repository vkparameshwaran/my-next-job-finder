import { useState } from "react";
import Dropzone from "../components/Dropzone";
import { uploadResume } from "../api/client";
import type { AnalyzeResponse } from "../types";

interface Props {
  onAnalyzed: (response: AnalyzeResponse) => void;
}

export default function Upload({ onAnalyzed }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [roleDescription, setRoleDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async () => {
    if (!file) return;
    setSubmitting(true);
    setError(null);
    try {
      const response = await uploadResume(file, roleDescription || null);
      onAnalyzed(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Analyze your resume</h1>
        <p className="text-slate-600 mt-1">
          Upload a PDF or DOCX. Optionally paste a target role description to score
          keyword overlap.
        </p>
      </div>

      <Dropzone file={file} onFile={setFile} />

      <div>
        <label htmlFor="role-description" className="block text-sm font-medium text-slate-700 mb-1">
          Target role description (optional)
        </label>
        <textarea
          id="role-description"
          rows={6}
          value={roleDescription}
          onChange={(e) => setRoleDescription(e.target.value)}
          placeholder="Paste the JD here to get keyword overlap and JD-aware suggestions"
          className="w-full border border-slate-300 rounded-md p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <button
        type="button"
        onClick={onSubmit}
        disabled={!file || submitting}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 rounded-md transition"
      >
        {submitting ? "Analyzing — this may take 10-15 seconds…" : "Analyze resume"}
      </button>
    </div>
  );
}
