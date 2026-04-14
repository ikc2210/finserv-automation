from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from devin_dispatcher import create_devin_session, get_session_status
from github_client import fetch_open_issues
from models import Issue, IssueStatus
from slack_notifier import send_slack_notification

# In-memory issue store keyed by issue ID
issue_store: dict[int, Issue] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
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


async def _run_issue_pipeline() -> None:
    """Fetch GitHub issues and dispatch each to Devin sequentially."""
    issues = await fetch_open_issues()
    for issue in issues:
        issue.status = IssueStatus.in_progress
        issue_store[issue.id] = issue
        try:
            session_id = await create_devin_session(issue)
            issue.devin_session_id = session_id
        except Exception:
            issue.status = IssueStatus.needs_human
            await send_slack_notification(issue)


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

    status = session_data.get("status", "")
    if status == "finished" and issue.status == IssueStatus.in_progress:
        # Check if a PR was opened based on structured output or URL
        pr_url = session_data.get("structured_output", {}).get("pr_url")
        if not pr_url:
            pr_url = session_data.get("result", {}).get("pr_url")

        if pr_url:
            issue.status = IssueStatus.pr_opened
            issue.pr_url = pr_url
            await send_slack_notification(issue)
        else:
            issue.status = IssueStatus.needs_human
            await send_slack_notification(issue)
    elif (status == "stopped" or status == "failed") and issue.status == IssueStatus.in_progress:
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
            session_id = await create_devin_session(issue)
            issue.devin_session_id = session_id
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
