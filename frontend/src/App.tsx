import { useState } from "react";
import { Routes, Route, Link, useNavigate, Navigate } from "react-router-dom";
import Upload from "./pages/Upload";
import Review from "./pages/Review";
import type { AnalyzeResponse } from "./types";

export default function App() {
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const navigate = useNavigate();

  const onAnalyzed = (response: AnalyzeResponse) => {
    setAnalysis(response);
    navigate("/review");
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="text-xl font-semibold text-slate-900">
            My Next Job Finder
          </Link>
          <span className="text-sm text-slate-500">Resume analyzer</span>
        </div>
      </header>
      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Upload onAnalyzed={onAnalyzed} />} />
          <Route
            path="/review"
            element={
              analysis ? <Review analysis={analysis} /> : <Navigate to="/" replace />
            }
          />
        </Routes>
      </main>
      <footer className="bg-white border-t border-slate-200">
        <div className="max-w-5xl mx-auto px-6 py-3 text-xs text-slate-500">
          v0.1.0
        </div>
      </footer>
    </div>
  );
}
