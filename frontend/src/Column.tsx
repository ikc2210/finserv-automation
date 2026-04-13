import type { Issue } from "./types";
import IssueCard from "./IssueCard";

interface ColumnProps {
  title: string;
  issues: Issue[];
  color: string;
}

export default function Column({ title, issues, color }: ColumnProps) {
  return (
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          {title}
        </h2>
        <span
          className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold text-white ${color}`}
        >
          {issues.length}
        </span>
      </div>
      <div className="bg-gray-100 rounded-lg p-3 min-h-[400px]">
        {issues.length === 0 ? (
          <p className="text-xs text-gray-400 text-center mt-8">No issues</p>
        ) : (
          issues.map((issue) => <IssueCard key={issue.id} issue={issue} />)
        )}
      </div>
    </div>
  );
}
