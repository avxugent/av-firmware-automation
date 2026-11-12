"""Turn a Release into a Jira parent task plus subtasks (idempotent)."""
from __future__ import annotations

from .jira import JiraClient, adf
from .models import Release


def parent_fields(release: Release, cfg: dict) -> dict:
    jira = cfg["jira"]
    lines = [
        f"New firmware release detected: {release.vendor} {release.model} {release.version}",
        f"Release date: {release.date or 'unknown'}",
        f"Release notes: {release.notes_url or 'n/a'}",
        f"Detected via: {release.source}",
        "Created by av-firmware-automation.",
    ]
    return {
        "project": {"key": jira["project_key"]},
        "issuetype": {"name": jira["parent_issue_type"]},
        "summary": release.summary,
        "description": adf("\n".join(lines)),
        "labels": [release.label, *jira.get("extra_labels", [])],
    }


def subtask_fields(parent_key: str, release: Release, cfg: dict, item: dict) -> dict:
    jira = cfg["jira"]
    return {
        "project": {"key": jira["project_key"]},
        "issuetype": {"name": jira["subtask_issue_type"]},
        "parent": {"key": parent_key},
        "summary": f"{item['summary']} ({release.model} {release.version})",
        "description": adf(item.get("description", "")),
    }


def run(release: Release, cfg: dict, template: list[dict],
        client: JiraClient | None, apply: bool) -> dict:
    """Create the ticket tree. Returns a report dict; never writes unless apply=True."""
    project = cfg["jira"]["project_key"]
    report = {"release": release.summary, "label": release.label, "applied": apply}

    if client is not None:
        existing = client.find_by_label(project, release.label)
        if existing:
            report.update(status="exists", parent=existing, subtasks=[])
            return report

    parent = parent_fields(release, cfg)
    subtasks = [subtask_fields("<PARENT>", release, cfg, item) for item in template]

    if not apply or client is None:
        report.update(status="dry-run", parent=parent, subtasks=subtasks)
        return report

    parent_key = client.create_issue(parent)
    created = [
        client.create_issue(subtask_fields(parent_key, release, cfg, item))
        for item in template
    ]
    report.update(status="created", parent=parent_key, subtasks=created)
    return report
