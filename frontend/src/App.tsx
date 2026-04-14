import { useState, useEffect, useCallback } from "react";
import type { Issue } from "./types";
import { fetchIssues, runPipeline } from "./api";
import Column from "./Column";

export default function App() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadIssues = useCallback(async () => {
    try {
      const data = await fetchIssues();
      setIssues(data);
      setError(null);
    } catch {
      setError("Cannot reach backend — retrying…");
    }
  }, []);

  useEffect(() => {
    loadIssues();
    const interval = setInterval(loadIssues, 5000);
    return () => clearInterval(interval);
  }, [loadIssues]);

  const handleRun = async () => {
    setRunning(true);
    try {
      await runPipeline();
    } catch {
      setError("Pipeline request failed");
    } finally {
      setRunning(false);
    }
  };

  const flagged = issues.filter((i) => i.status === "flagged");
  const inProgress = issues.filter((i) => i.status === "in_progress");
  const prOpened = issues.filter((i) => i.status === "pr_opened");
  const needsHuman = issues.filter((i) => i.status === "needs_human");

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#0f1117" }}>
      {/* Header */}
      <header
        className="text-white px-8 py-5 flex items-center justify-between border-b"
        style={{ backgroundColor: "#0a0c12", borderColor: "#1e2130" }}
      >
        <h1
          className="text-white"
          style={{ fontSize: "22px", fontWeight: 300, letterSpacing: "0.12em" }}
        >
          FinServ Issue Autopilot
        </h1>
        <button
          onClick={handleRun}
          disabled={running}
          className="px-5 py-2 bg-transparent border border-white/60 text-white/90 text-sm font-normal rounded-lg transition-all cursor-pointer disabled:cursor-not-allowed disabled:opacity-40 hover:border-white hover:text-white hover:bg-white/5 flex items-center gap-2"
          style={{ fontWeight: 400 }}
        >
          {running && (
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          )}
          Run Pipeline
        </button>
      </header>

      {/* Error banner */}
      {error && (
        <div
          className="border-b px-8 py-2 text-sm"
          style={{
            backgroundColor: "#1a1610",
            borderColor: "#3d3520",
            color: "#d4a543",
          }}
        >
          {error}
        </div>
      )}

      {/* Columns */}
      <main className="p-6 flex gap-5">
        <Column title="Flagged" issues={flagged} accent="#3b82f6" />
        <Column title="In Progress" issues={inProgress} accent="#f59e0b" />
        <Column title="PR Opened" issues={prOpened} accent="#10b981" />
        <Column title="Needs Human" issues={needsHuman} accent="#ef4444" />
      </main>
    </div>
  );
}
