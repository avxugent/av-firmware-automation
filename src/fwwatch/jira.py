"""Minimal Jira Cloud REST client (v3). Only what the pipeline needs."""

from __future__ import annotations

import requests


def adf(text: str) -> dict:
    """Wrap plain text in Atlassian Document Format (one paragraph per line)."""
    paragraphs = [
        {"type": "paragraph", "content": [{"type": "text", "text": line}]}
        for line in text.splitlines()
        if line.strip()
    ] or [{"type": "paragraph", "content": []}]
    return {"type": "doc", "version": 1, "content": paragraphs}


class JiraClient:
    def __init__(self, base_url: str, email: str, token: str, session=None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.auth = (email, token)
        self.session.headers.update({"Accept": "application/json"})

    def find_by_label(self, project: str, label: str) -> str | None:
        """Return the key of an existing issue with this label, or None."""
        jql = f'project = "{project}" AND labels = "{label}" ORDER BY created ASC'
        resp = self.session.post(
            f"{self.base_url}/rest/api/3/search/jql",
            json={"jql": jql, "fields": ["key"], "maxResults": 1},
            timeout=30,
        )
        resp.raise_for_status()
        issues = resp.json().get("issues", [])
        return issues[0]["key"] if issues else None

    def create_issue(self, fields: dict) -> str:
        resp = self.session.post(
            f"{self.base_url}/rest/api/3/issue",
            json={"fields": fields},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["key"]
