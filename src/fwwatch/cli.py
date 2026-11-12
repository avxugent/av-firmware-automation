"""Command line entry point: python -m fwwatch ..."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from .jira import JiraClient
from .models import Release
from .pipeline import run

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="fwwatch", description=__doc__)
    p.add_argument("--vendor", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--notes-url", default="")
    p.add_argument("--date", default="")
    p.add_argument("--config", default=str(ROOT / "config.yaml"))
    p.add_argument("--template", default=str(ROOT / "templates" / "subtasks.yaml"))
    p.add_argument(
        "--apply", action="store_true", help="Actually create Jira issues (default is a dry run)"
    )
    args = p.parse_args(argv)

    cfg = yaml.safe_load(Path(args.config).read_text())
    template = yaml.safe_load(Path(args.template).read_text())["subtasks"]
    release = Release(args.vendor, args.model, args.version, args.notes_url, args.date)

    email, token = os.environ.get("JIRA_EMAIL"), os.environ.get("JIRA_API_TOKEN")
    client = None
    if email and token:
        client = JiraClient(cfg["jira"]["base_url"], email, token)
    elif args.apply:
        print("--apply needs JIRA_EMAIL and JIRA_API_TOKEN", file=sys.stderr)
        return 2

    report = run(release, cfg, template, client, apply=args.apply)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
