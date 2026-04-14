import os

import httpx

from models import Issue, IssueStatus


SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


async def send_slack_notification(
    issue: Issue, base_url: str = "http://localhost:8000"
) -> None:
    """Send a Slack notification based on the issue status."""
    if not SLACK_WEBHOOK_URL:
        return

    if issue.status == IssueStatus.pr_opened:
        payload = _build_pr_opened_message(issue)
    elif issue.status == IssueStatus.needs_human:
        payload = _build_needs_human_message(issue, base_url)
    else:
        return

    async with httpx.AsyncClient() as client:
        await client.post(SLACK_WEBHOOK_URL, json=payload)


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
    """Build a Slack message for a needs_human event with action buttons."""
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
                        "This issue was flagged as too complex or risky for automated resolution."
                    ),
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Automate it"},
                        "style": "primary",
                        "url": f"{base_url}/api/issues/{issue.id}/override",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Dismiss"},
                        "style": "danger",
                        "url": f"{base_url}/api/issues/{issue.id}/dismiss",
                    },
                ],
            },
        ],
    }
