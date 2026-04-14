import type { Issue } from "./types";
import IssueCard from "./IssueCard";

interface ColumnProps {
  title: string;
  issues: Issue[];
  accent: string;
}

export default function Column({ title, issues, accent }: ColumnProps) {
  return (
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-3 mb-4">
        <h2
          className="text-xs uppercase"
          style={{
            fontWeight: 500,
            letterSpacing: "0.08em",
            color: "#6b7280",
          }}
        >
          {title}
        </h2>
        <span
          className="inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs"
          style={{
            backgroundColor: "#1e2130",
            color: "#6b7280",
            fontWeight: 400,
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          {issues.length}
        </span>
      </div>
      <div
        className="rounded-lg p-3 min-h-[400px]"
        style={{ backgroundColor: "#13151e" }}
      >
        {issues.length === 0 ? (
          <p className="text-xs text-center mt-8" style={{ color: "#3d4050" }}>
            No issues
          </p>
        ) : (
          issues.map((issue) => (
            <IssueCard key={issue.id} issue={issue} accent={accent} />
          ))
        )}
      </div>
    </div>
  );
}
