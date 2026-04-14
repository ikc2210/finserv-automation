import type { Issue } from "./types";
import { overrideIssue } from "./api";

function labelStyle(label: string): React.CSSProperties {
  switch (label) {
    case "bug":
      return { backgroundColor: "#2a1215", color: "#f87171" };
    case "enhancement":
      return { backgroundColor: "#111827", color: "#60a5fa" };
    case "stale":
      return { backgroundColor: "#1c1c22", color: "#6b7280" };
    default:
      return { backgroundColor: "#1c1c22", color: "#6b7280" };
  }
}

function riskBarColor(score: number): string {
  if (score <= 4) return "#10b981";
  if (score <= 7) return "#f59e0b";
  return "#ef4444";
}

function complexityStyle(complexity: string): React.CSSProperties {
  switch (complexity) {
    case "low":
      return { backgroundColor: "#0d2818", color: "#34d399" };
    case "medium":
      return { backgroundColor: "#2a1f0a", color: "#fbbf24" };
    case "high":
      return { backgroundColor: "#2a1215", color: "#f87171" };
    default:
      return { backgroundColor: "#1c1c22", color: "#6b7280" };
  }
}

interface IssueCardProps {
  issue: Issue;
  accent: string;
}

export default function IssueCard({ issue, accent }: IssueCardProps) {
  return (
    <div
      className="rounded-lg mb-3 transition-all hover:brightness-110"
      style={{
        backgroundColor: "#1a1d27",
        padding: "16px 18px",
        borderLeft: `3px solid ${accent}`,
        borderRadius: "8px",
      }}
    >
      {/* Issue number + title + spinner */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <span
            className="text-xs"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              color: "#4b5060",
              fontWeight: 400,
            }}
          >
            #{issue.number}
          </span>
          <a
            href={`https://github.com/ikc2210/finserv-monorepo-demo/issues/${issue.number}`}
            target="_blank"
            rel="noopener noreferrer"
            className="leading-tight mt-1 block no-underline hover:opacity-80"
            style={{
              fontSize: "13px",
              fontWeight: 500,
              color: "#e2e4ea",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
              textDecoration: "none",
            }}
          >
            {issue.title}
          </a>
        </div>
        {issue.status === "in_progress" && (
          <div className="ml-3 flex-shrink-0">
            <svg
              className="animate-spin h-4 w-4"
              style={{ color: accent }}
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

      {/* Labels */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {issue.labels.map((label) => (
          <span
            key={label}
            className="px-2 py-0.5 rounded-full"
            style={{
              fontSize: "10px",
              fontWeight: 400,
              ...labelStyle(label),
            }}
          >
            {label}
          </span>
        ))}
      </div>

      {/* Risk score bar + complexity */}
      <div className="flex items-center gap-3 mb-3">
        <div className="flex items-center gap-2 flex-1">
          <div
            className="flex-1 rounded-full overflow-hidden"
            style={{ height: "4px", backgroundColor: "#252836" }}
          >
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${issue.risk_score * 10}%`,
                backgroundColor: riskBarColor(issue.risk_score),
              }}
            />
          </div>
          <span
            className="text-xs"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              color: riskBarColor(issue.risk_score),
              fontWeight: 500,
              minWidth: "20px",
            }}
          >
            {issue.risk_score}
          </span>
        </div>
        <span
          className="px-2 py-0.5 rounded"
          style={{
            fontSize: "10px",
            fontWeight: 400,
            ...complexityStyle(issue.complexity),
          }}
        >
          {issue.complexity}
        </span>
      </div>

      {/* Links */}
      <div className="flex flex-col gap-1.5">
        {issue.pr_url && (
          <a
            href={issue.pr_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs hover:underline truncate"
            style={{ color: "#60a5fa", fontWeight: 400 }}
          >
            View Pull Request →
          </a>
        )}
        {issue.devin_session_id && (
          <a
            href={`https://app.devin.ai/sessions/${issue.devin_session_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs hover:underline truncate"
            style={{ color: "#a78bfa", fontWeight: 400 }}
          >
            View Devin Session →
          </a>
        )}
      </div>

      {/* Needs Human actions */}
      {issue.status === "needs_human" && (
        <div
          className="mt-3 pt-3 flex gap-2"
          style={{ borderTop: "1px solid #252836" }}
        >
          <button
            onClick={() => overrideIssue(issue.id)}
            className="flex-1 px-3 py-1.5 bg-transparent text-xs rounded transition-all cursor-pointer"
            style={{
              border: "1px solid #10b98150",
              color: "#10b981",
              fontWeight: 400,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#10b98110";
              e.currentTarget.style.borderColor = "#10b981";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
              e.currentTarget.style.borderColor = "#10b98150";
            }}
          >
            Automate it
          </button>
          <button
            className="flex-1 px-3 py-1.5 bg-transparent text-xs rounded transition-all cursor-pointer"
            style={{
              border: "1px solid #4b506050",
              color: "#6b7280",
              fontWeight: 400,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#4b506010";
              e.currentTarget.style.borderColor = "#6b7280";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
              e.currentTarget.style.borderColor = "#4b506050";
            }}
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
}
