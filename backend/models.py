from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IssueStatus(str, Enum):
    flagged = "flagged"
    in_progress = "in_progress"
    pr_opened = "pr_opened"
    needs_human = "needs_human"
    dismissed = "dismissed"


class Issue(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    url: str
    status: IssueStatus = IssueStatus.flagged
    labels: list[str] = []
    risk_score: int = 0
    complexity: str = "low"
    devin_session_id: Optional[str] = None
    devin_session_url: Optional[str] = None
    pr_url: Optional[str] = None


class TriageResult(BaseModel):
    issue_id: int
    complexity: str
    risk_score: int
    action: str
    explanation: Optional[str] = None
