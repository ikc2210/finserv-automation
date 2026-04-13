import type { Issue } from "./types";
import { overrideIssue } from "./api";

function labelColor(label: string): string {
  switch (label) {
    case "bug":
      return "bg-red-500 text-white";
    case "enhancement":
      return "bg-blue-500 text-white";
    case "stale":
      return "bg-gray-400 text-white";
    default:
      return "bg-gray-300 text-gray-800";
  }
}

function riskColor(score: number): string {
  if (score <= 4) return "text-green-600";
  if (score <= 7) return "text-yellow-500";
  return "text-red-600";
}

function complexityStyle(complexity: string): string {
  switch (complexity) {
    case "low":
      return "bg-green-100 text-green-800";
    case "medium":
      return "bg-yellow-100 text-yellow-800";
    case "high":
      return "bg-red-100 text-red-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
}

export default function IssueCard({ issue }: { issue: Issue }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-3">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <span className="text-xs font-mono text-gray-400">#{issue.number}</span>
          <h3 className="text-sm font-medium text-gray-900 leading-tight mt-0.5 truncate">
            {issue.title}
          </h3>
        </div>
        {issue.status === "in_progress" && (
          <div className="ml-2 flex-shrink-0">
            <svg
              className="animate-spin h-4 w-4 text-blue-500"
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
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {issue.labels.map((label) => (
          <span
            key={label}
            className={`px-2 py-0.5 rounded-full text-xs font-medium ${labelColor(label)}`}
          >
            {label}
          </span>
        ))}
      </div>

      <div className="flex items-center gap-3 mb-3">
        <span className={`text-sm font-semibold ${riskColor(issue.risk_score)}`}>
          Risk: {issue.risk_score}/10
        </span>
        <span
          className={`px-2 py-0.5 rounded text-xs font-medium ${complexityStyle(issue.complexity)}`}
        >
          {issue.complexity}
        </span>
      </div>

      <div className="flex flex-col gap-1.5">
        {issue.pr_url && (
          <a
            href={issue.pr_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-600 hover:text-blue-800 hover:underline truncate"
          >
            View Pull Request →
          </a>
        )}
        {issue.devin_session_id && (
          <a
            href={`https://app.devin.ai/sessions/${issue.devin_session_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-purple-600 hover:text-purple-800 hover:underline truncate"
          >
            View Devin Session →
          </a>
        )}
      </div>

      {issue.status === "needs_human" && (
        <div className="mt-3 pt-3 border-t border-gray-100 flex gap-2">
          <button
            onClick={() => overrideIssue(issue.id)}
            className="flex-1 px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Automate it
          </button>
          <button className="flex-1 px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-medium rounded hover:bg-gray-300 transition-colors cursor-pointer">
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
}
