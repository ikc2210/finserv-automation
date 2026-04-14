import os

import httpx

from models import Issue


DEVIN_API_KEY = os.getenv("DEVIN_API_KEY", "")
DEVIN_API_BASE = "https://api.devin.ai/v1"


async def create_devin_session(issue: Issue) -> str:
    """Create a Devin session to investigate and potentially fix a GitHub issue.

    Returns the Devin session ID.
    """
    prompt = (
        f"Investigate GitHub issue #{issue.number}: {issue.title}\n\n"
        f"Issue URL: {issue.url}\n\n"
        f"Description:\n{issue.body or 'No description provided.'}\n\n"
        "Instructions:\n"
        "1. Assess the complexity (low, medium, high) and risk (1-10 scale) of this issue.\n"
        "2. If complexity is low or medium AND risk is below 7, implement a fix and open a PR.\n"
        "3. If complexity is high OR risk is 7 or above, flag the issue for human review.\n"
        "4. Provide a brief explanation of your assessment."
    )

    headers = {
        "Authorization": f"Bearer {DEVIN_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"prompt": prompt}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DEVIN_API_BASE}/sessions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data["session_id"]


async def get_session_status(session_id: str) -> dict:
    """Poll the status of a Devin session.

    Returns the session status data including status and any PR URL.
    """
    headers = {
        "Authorization": f"Bearer {DEVIN_API_KEY}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DEVIN_API_BASE}/sessions/{session_id}",
            headers=headers,
        )
        response.raise_for_status()

    return response.json()
