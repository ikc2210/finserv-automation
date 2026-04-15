import os

import httpx

from models import Issue


GITHUB_API_BASE = "https://api.github.com"


async def fetch_open_issues() -> list[Issue]:
    """Fetch open issues from the configured GitHub repository, skipping PRs."""
    github_token = os.getenv("GITHUB_TOKEN", "")
    github_repo = os.getenv("GITHUB_REPO", "")
    url = f"{GITHUB_API_BASE}/repos/{github_repo}/issues"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    params = {"state": "open", "per_page": 100}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        raw_issues = response.json()

    issues: list[Issue] = []
    for raw in raw_issues:
        # Skip pull requests — GitHub returns PRs in the issues endpoint
        if "pull_request" in raw:
            continue

        issue = Issue(
            id=raw["id"],
            number=raw["number"],
            title=raw["title"],
            body=raw.get("body"),
            url=raw["html_url"],
            labels=[lbl["name"] for lbl in raw.get("labels", [])],
        )
        issues.append(issue)

    return issues
