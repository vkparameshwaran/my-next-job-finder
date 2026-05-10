import type { AnalyzeResponse, Suggestion } from "../types";

const BASE = "/api";

export async function uploadResume(
  file: File,
  roleDescription: string | null,
): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (roleDescription) {
    formData.append("role_description", roleDescription);
  }
  const res = await fetch(`${BASE}/resume/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Upload failed (${res.status}): ${detail}`);
  }
  return res.json();
}

export async function exportResume(
  recordId: string,
  acceptedSuggestions: Suggestion[],
  filename = "resume-tweaked.docx",
): Promise<void> {
  const res = await fetch(`${BASE}/resume/${recordId}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(acceptedSuggestions),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Export failed (${res.status}): ${detail}`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
