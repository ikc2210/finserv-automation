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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-md">
        <h1 className="text-xl font-bold tracking-tight">FinServ Issue Autopilot</h1>
        <button
          onClick={handleRun}
          disabled={running}
          className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed flex items-center gap-2"
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
        <div className="bg-yellow-50 border-b border-yellow-200 px-6 py-2 text-sm text-yellow-800">
          {error}
        </div>
      )}

      {/* Columns */}
      <main className="p-6 flex gap-4">
        <Column title="Flagged" issues={flagged} color="bg-yellow-500" />
        <Column title="In Progress" issues={inProgress} color="bg-blue-500" />
        <Column title="PR Opened" issues={prOpened} color="bg-green-500" />
        <Column title="Needs Human" issues={needsHuman} color="bg-red-500" />
      </main>
    </div>
  );
}
