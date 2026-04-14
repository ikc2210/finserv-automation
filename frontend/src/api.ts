const API_BASE = "http://localhost:8000/api";

export async function fetchIssues() {
  const res = await fetch(`${API_BASE}/issues`);
  if (!res.ok) throw new Error(`Failed to fetch issues: ${res.status}`);
  return res.json();
}

export async function runPipeline() {
  const res = await fetch(`${API_BASE}/run`, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to run pipeline: ${res.status}`);
  return res.json();
}

export async function overrideIssue(id: number) {
  const res = await fetch(`${API_BASE}/issues/${id}/override`, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to override issue: ${res.status}`);
  return res.json();
}
