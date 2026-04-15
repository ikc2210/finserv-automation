export interface Issue {
  id: number;
  number: number;
  title: string;
  body?: string;
  labels: string[];
  status: "flagged" | "in_progress" | "pr_opened" | "needs_human" | "dismissed";
  risk_score: number;
  complexity: "low" | "medium" | "high";
  pr_url?: string;
  devin_session_id?: string;
  devin_session_url?: string;
}
