# av-firmware-automation

Creates a Jira ticket tree (parent task + subtasks) in project `RECORD` when a new AV device
firmware release is reported. Dry run by default.

## Status (Phase 1)
- Release input: **manual trigger only** (GitHub Actions `workflow_dispatch`, or the CLI).
  Epiphan's docs site blocks automated fetches, so detection adapters (email lists, vendor API)
  come in Phase 2.
- Dedup: a `fw-<vendor>-<model>-<version>` label on the parent; re-running creates nothing.
- Not yet built: Confluence draft, Grafana baseline PR, per-device tasks (see the plan).

## Usage
```bash
pip install -r requirements.txt
PYTHONPATH=src python -m fwwatch --vendor Epiphan --model Pearl-2 --version 4.24.4   # dry run
JIRA_EMAIL=... JIRA_API_TOKEN=... PYTHONPATH=src python -m fwwatch ... --apply        # real
```

GitHub secrets needed: `JIRA_EMAIL`, `JIRA_API_TOKEN`.

## Tests
```bash
python -m unittest discover -s tests
```

Subtask list: `templates/subtasks.yaml`. Project and issue types: `config.yaml`.
