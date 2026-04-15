import asyncio
import logging
import os

import httpx

from models import Issue


DEVIN_API_BASE = "https://api.devin.ai/v1"

logger = logging.getLogger(__name__)

_MAX_RETRIES = 5
_BASE_BACKOFF = 60.0  # seconds — Devin rate limit window is on the order of minutes


async def create_devin_session(issue: Issue) -> str:
    """Create a Devin session to investigate and potentially fix a GitHub issue.

    Returns the Devin session ID. Retries on 429 with Retry-After or exponential backoff.
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
        "Authorization": f"Bearer {os.getenv('DEVIN_API_KEY', '')}",
        "Content-Type": "application/json",
    }
    payload = {"prompt": prompt}

    async with httpx.AsyncClient() as client:
        for attempt in range(_MAX_RETRIES):
            response = await client.post(
                f"{DEVIN_API_BASE}/sessions",
                headers=headers,
                json=payload,
            )
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else _BASE_BACKOFF * (2 ** attempt)
                logger.warning(
                    "Devin rate limit hit for issue #%s (attempt %d/%d), waiting %.1fs",
                    issue.number, attempt + 1, _MAX_RETRIES, wait,
                )
                await asyncio.sleep(wait)
                continue
            response.raise_for_status()
            data = response.json()
            logger.info("Devin session created for issue #%s: %s", issue.number, data)
            return data["session_id"], data.get("url")

    raise RuntimeError(f"Devin rate limit exceeded after {_MAX_RETRIES} retries for issue #{issue.number}")


async def get_session_status(session_id: str) -> dict:
    """Poll the status of a Devin session.

    Returns the session status data including status and any PR URL.
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('DEVIN_API_KEY', '')}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DEVIN_API_BASE}/sessions/{session_id}",
            headers=headers,
        )
        response.raise_for_status()

    return response.json()
