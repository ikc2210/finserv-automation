import asyncio
import logging
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from devin_dispatcher import create_devin_session, get_session_status
from github_client import fetch_open_issues
from models import Issue, IssueStatus
from slack_notifier import send_slack_notification



# In-memory issue store keyed by issue ID
issue_store: dict[int, Issue] = {}


_POLL_INTERVAL = 30.0  # seconds between status checks


def _parse_devin_assessment(messages: list[dict]) -> tuple[str, int]:
    """Extract complexity (low/medium/high) and risk_score (1-10) from Devin's last message."""
    text = ""
    for msg in reversed(messages):
        if msg.get("type") == "devin_message":
            text = msg.get("message", "")
            break
    if not text:
        return "low", 0

    complexity = "low"
    m = re.search(r"complexity[:\s*]+(\w+)", text, re.IGNORECASE)
    if m and m.group(1).lower() in ("high", "medium", "low"):
        complexity = m.group(1).lower()

    risk_score = 0
    m = re.search(r"risk[:\s*]+(\d+)(?:/10)?", text, re.IGNORECASE)
    if m:
        risk_score = min(10, max(0, int(m.group(1))))

    return complexity, risk_score


def _is_flagged_for_human(messages: list[dict]) -> bool:
    """Return True if Devin's last message flags the issue for human review."""
    for msg in reversed(messages):
        if msg.get("type") == "devin_message":
            text = msg.get("message", "").lower()
            return bool(re.search(r"flag|human review", text))
    return False


async def _poll_in_progress_issues() -> None:
    """Background task that polls Devin for all in-progress issues."""
    while True:
        await asyncio.sleep(_POLL_INTERVAL)
        in_progress = [
            issue for issue in issue_store.values()
            if issue.status == IssueStatus.in_progress and issue.devin_session_id
        ]
        for issue in in_progress:
            try:
                session_data = await get_session_status(issue.devin_session_id)
            except Exception as e:
                logger.warning("Failed to poll Devin for issue #%s: %s", issue.number, e)
                continue

            status_enum = session_data.get("status_enum", "")
            pr_url = (session_data.get("pull_request") or {}).get("url")
            messages = session_data.get("messages", [])

            complexity, risk_score = _parse_devin_assessment(messages)
            issue.complexity = complexity
            issue.risk_score = risk_score

            if pr_url:
                issue.status = IssueStatus.pr_opened
                issue.pr_url = pr_url
                await send_slack_notification(issue)
            elif status_enum in ("blocked", "stopped", "failed") or _is_flagged_for_human(messages):
                issue.status = IssueStatus.needs_human
                await send_slack_notification(issue)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task = asyncio.create_task(_poll_in_progress_issues())
    yield
    task.cancel()
    issue_store.clear()


app = FastAPI(title="FinServ Issue Automation", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/issues")
async def list_issues() -> list[Issue]:
    """Return all issues from the in-memory store."""
    return list(issue_store.values())


_INTER_ISSUE_DELAY = 30.0  # seconds between Devin session creations


async def _run_issue_pipeline() -> None:
    """Fetch GitHub issues and dispatch each to Devin sequentially."""
    issues = await fetch_open_issues()
    for i, issue in enumerate(issues):
        issue.status = IssueStatus.in_progress
        issue_store[issue.id] = issue
        try:
            session_id, session_url = await create_devin_session(issue)
            issue.devin_session_id = session_id
            issue.devin_session_url = session_url
        except Exception as e:
            logger.error("Failed to create Devin session for issue #%s: %s", issue.number, e)
            issue.status = IssueStatus.needs_human
            await send_slack_notification(issue)
        if i < len(issues) - 1:
            await asyncio.sleep(_INTER_ISSUE_DELAY)


@app.post("/api/run")
async def run_pipeline(background_tasks: BackgroundTasks) -> dict:
    """Fetch GitHub issues and dispatch each to Devin in the background."""
    background_tasks.add_task(_run_issue_pipeline)
    return {"message": "Pipeline started"}


@app.get("/api/issues/{issue_id}/status")
async def get_issue_status(issue_id: int) -> Issue:
    """Poll the Devin session status for a given issue and update the store."""
    if issue_id not in issue_store:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue = issue_store[issue_id]

    if not issue.devin_session_id:
        return issue

    try:
        session_data = await get_session_status(issue.devin_session_id)
    except Exception:
        return issue

    status_enum = session_data.get("status_enum", "")
    pr_url = (session_data.get("pull_request") or {}).get("url")
    messages = session_data.get("messages", [])

    complexity, risk_score = _parse_devin_assessment(messages)
    issue.complexity = complexity
    issue.risk_score = risk_score

    if pr_url and issue.status == IssueStatus.in_progress:
        issue.status = IssueStatus.pr_opened
        issue.pr_url = pr_url
        await send_slack_notification(issue)
    elif (
        status_enum in ("blocked", "stopped", "failed") or _is_flagged_for_human(messages)
    ) and issue.status == IssueStatus.in_progress:
        issue.status = IssueStatus.needs_human
        await send_slack_notification(issue)

    issue_store[issue_id] = issue
    return issue


@app.post("/api/issues/{issue_id}/override")
async def override_issue(issue_id: int, background_tasks: BackgroundTasks) -> dict:
    """Dispatch a needs_human issue to Devin anyway."""
    if issue_id not in issue_store:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue = issue_store[issue_id]
    if issue.status != IssueStatus.needs_human:
        raise HTTPException(
            status_code=400,
            detail="Only needs_human issues can be overridden",
        )

    issue.status = IssueStatus.in_progress
    issue_store[issue_id] = issue

    async def _dispatch_override() -> None:
        try:
            session_id, session_url = await create_devin_session(issue)
            issue.devin_session_id = session_id
            issue.devin_session_url = session_url
        except Exception:
            issue.status = IssueStatus.needs_human

    background_tasks.add_task(_dispatch_override)
    return {"message": f"Issue {issue_id} overridden, dispatching to Devin"}


@app.post("/api/issues/{issue_id}/dismiss")
async def dismiss_issue(issue_id: int) -> dict:
    """Mark an issue as dismissed."""
    if issue_id not in issue_store:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue = issue_store[issue_id]
    issue.status = IssueStatus.dismissed
    issue_store[issue_id] = issue
    return {"message": f"Issue {issue_id} dismissed"}
