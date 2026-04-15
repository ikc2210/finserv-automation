import os

import httpx

from models import Issue, IssueStatus


async def send_slack_notification(
    issue: Issue, base_url: str = "http://localhost:5173"
) -> None:
    """Send a Slack notification based on the issue status."""
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
    if not slack_webhook_url:
        return

    if issue.status == IssueStatus.pr_opened:
        payload = _build_pr_opened_message(issue)
    elif issue.status == IssueStatus.needs_human:
        payload = _build_needs_human_message(issue, base_url)
    else:
        return

    async with httpx.AsyncClient() as client:
        await client.post(slack_webhook_url, json=payload)


def _build_pr_opened_message(issue: Issue) -> dict:
    """Build a Slack message for a PR opened event."""
    return {
        "text": f"🤖 PR opened for issue #{issue.number}: {issue.title}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*PR Opened* for issue "
                        f"<{issue.url}|#{issue.number}: {issue.title}>\n\n"
                        f"PR: {issue.pr_url or 'N/A'}"
                    ),
                },
            },
        ],
    }


def _build_needs_human_message(issue: Issue, base_url: str) -> dict:
    """Build a Slack message for a needs_human event."""
    return {
        "text": f"🚨 Issue #{issue.number} needs human review: {issue.title}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Needs Human Review*: "
                        f"<{issue.url}|#{issue.number}: {issue.title}>\n\n"
                        f"This issue was flagged as too complex or risky for automated resolution. "
                        f"<{base_url}|View in dashboard> to override or dismiss."
                    ),
                },
            },
        ],
    }
