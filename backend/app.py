"""FinServ Issue Autopilot — Backend API.

Provides endpoints for the dashboard frontend to fetch issues,
trigger the automation pipeline, and override issues flagged for
human review.
"""

from __future__ import annotations

import random
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FinServ Issue Autopilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

VALID_STATUSES = {"flagged", "in_progress", "pr_opened", "needs_human"}
VALID_COMPLEXITIES = {"low", "medium", "high"}


class Issue(BaseModel):
    id: int
    number: int
    title: str
    labels: list[str]
    status: str
    risk_score: int
    complexity: str
    pr_url: str | None = None
    devin_session_id: str | None = None


# ---------------------------------------------------------------------------
# In-memory store — seeded with realistic data from finserv-monorepo-demo
# ---------------------------------------------------------------------------

_SEED_ISSUES: list[dict[str, Any]] = [
    {
        "id": 1,
        "number": 21,
        "title": "payment validation blows up on certain currencies",
        "labels": ["bug"],
        "status": "flagged",
        "risk_score": 3,
        "complexity": "low",
    },
    {
        "id": 2,
        "number": 22,
        "title": "encryption.py is not actually encrypting anything",
        "labels": ["bug"],
        "status": "flagged",
        "risk_score": 8,
        "complexity": "medium",
    },
    {
        "id": 3,
        "number": 23,
        "title": "add pagination metadata to list endpoints",
        "labels": ["enhancement"],
        "status": "in_progress",
        "risk_score": 2,
        "complexity": "low",
        "devin_session_id": "abc123-session-demo",
    },
    {
        "id": 4,
        "number": 24,
        "title": "transfers sometimes lose money",
        "labels": ["bug"],
        "status": "needs_human",
        "risk_score": 9,
        "complexity": "high",
    },
    {
        "id": 5,
        "number": 25,
        "title": "CORS is set to allow all origins",
        "labels": ["bug"],
        "status": "pr_opened",
        "risk_score": 4,
        "complexity": "low",
        "pr_url": "https://github.com/ikc2210/finserv-monorepo-demo/pull/42",
        "devin_session_id": "def456-session-demo",
    },
    {
        "id": 6,
        "number": 26,
        "title": "webhook notifications for payment status changes",
        "labels": ["enhancement", "stale"],
        "status": "flagged",
        "risk_score": 5,
        "complexity": "medium",
    },
    {
        "id": 7,
        "number": 27,
        "title": "close_account doesn't check for pending txns",
        "labels": ["bug"],
        "status": "in_progress",
        "risk_score": 6,
        "complexity": "medium",
        "devin_session_id": "ghi789-session-demo",
    },
    {
        "id": 8,
        "number": 28,
        "title": "something wrong with the rate limiter",
        "labels": ["bug", "stale"],
        "status": "flagged",
        "risk_score": 3,
        "complexity": "low",
    },
    {
        "id": 9,
        "number": 29,
        "title": "audit logging for compliance",
        "labels": ["enhancement"],
        "status": "needs_human",
        "risk_score": 7,
        "complexity": "high",
    },
    {
        "id": 10,
        "number": 30,
        "title": "datetime.utcnow() deprecation warnings everywhere",
        "labels": ["bug"],
        "status": "pr_opened",
        "risk_score": 1,
        "complexity": "low",
        "pr_url": "https://github.com/ikc2210/finserv-monorepo-demo/pull/43",
        "devin_session_id": "jkl012-session-demo",
    },
    {
        "id": 11,
        "number": 34,
        "title": "migrate to real postgres repos",
        "labels": ["enhancement"],
        "status": "needs_human",
        "risk_score": 10,
        "complexity": "high",
    },
    {
        "id": 12,
        "number": 35,
        "title": "fraud velocity state resets on every deploy",
        "labels": ["bug"],
        "status": "in_progress",
        "risk_score": 6,
        "complexity": "medium",
        "devin_session_id": "mno345-session-demo",
    },
    {
        "id": 13,
        "number": 38,
        "title": "multi-currency support",
        "labels": ["enhancement"],
        "status": "needs_human",
        "risk_score": 10,
        "complexity": "high",
    },
    {
        "id": 14,
        "number": 39,
        "title": "replace fraud rules with ML model",
        "labels": ["enhancement"],
        "status": "needs_human",
        "risk_score": 9,
        "complexity": "high",
    },
    {
        "id": 15,
        "number": 40,
        "title": "payment service double-charges on retry",
        "labels": ["bug", "stale"],
        "status": "flagged",
        "risk_score": 7,
        "complexity": "medium",
    },
]

_issues: list[dict[str, Any]] = [dict(i) for i in _SEED_ISSUES]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/issues")
async def list_issues() -> list[dict[str, Any]]:
    """Return all tracked issues for the dashboard."""
    return _issues


@app.post("/api/run")
async def run_pipeline() -> dict[str, str]:
    """Trigger the automation pipeline.

    In a real deployment this would kick off Devin sessions for each
    flagged issue.  Here we simulate progress by randomly advancing
    a few flagged issues to in_progress.
    """
    advanced = 0
    for issue in _issues:
        if issue["status"] == "flagged" and random.random() < 0.5:
            issue["status"] = "in_progress"
            issue["devin_session_id"] = f"sim-{issue['id']}-{random.randint(1000,9999)}"
            advanced += 1
    return {"message": f"Pipeline started — {advanced} issues picked up"}


@app.post("/api/issues/{issue_id}/override")
async def override_issue(issue_id: int) -> dict[str, str]:
    """Move a needs_human issue back into the automation pipeline."""
    for issue in _issues:
        if issue["id"] == issue_id:
            if issue["status"] != "needs_human":
                raise HTTPException(
                    status_code=400,
                    detail=f"Issue {issue_id} is not in needs_human status",
                )
            issue["status"] = "in_progress"
            issue["devin_session_id"] = f"override-{issue_id}-{random.randint(1000,9999)}"
            return {"message": f"Issue #{issue['number']} moved back to automation"}
    raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
