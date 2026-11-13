# CLAUDE.md

Context and rules for AI assistants (and humans) working in this repo.

## What this project is
Automates the firmware update process for our AV devices. A reported firmware release becomes a
Jira parent task plus subtasks in project `RECORD` (site universiteitgent.atlassian.net).
Planned later phases: Confluence doc draft, Grafana baseline merge request, per-device tasks.
Phase 1 only has a manual trigger; vendor detection adapters (email, vendor API) come later.

## Layout
- `src/fwwatch/models.py`: `Release` dataclass; `label` is the dedup key (`fw-<vendor>-<model>-<version>`)
- `src/fwwatch/pipeline.py`: builds Jira payloads, `run()` is idempotent
- `src/fwwatch/jira.py`: thin Jira Cloud REST v3 client
- `src/fwwatch/cli.py`: CLI entry point (`python -m fwwatch`)
- `src/fwwatch/devices.py`: picks devices below a target firmware version (pure logic)
- `.claude/skills/firmware-device-tasks/`: Claude Code skill that creates per-device Jira tasks
  from SAM data (must run on a machine that can reach sam.ugent.be)
- `docs/jira-automation.md`: spec of the Jira Automation rules that create the release ticket tree
- `templates/subtasks.yaml`: the subtask list; edit this to change the process
- `config.yaml`: Jira project key and issue type names
- `.github/workflows/firmware-watch.yml`: manual trigger; `ci.yml`: checks on every PR

## Commands
```bash
pip install -r requirements.txt ruff
python -m unittest discover -s tests      # tests
ruff check . && ruff format --check .     # lint and format (ruff format . to fix)
PYTHONPATH=src python -m fwwatch --vendor X --model Y --version Z   # dry run
```

## Rules
- **Dry run is the default.** Never make code paths write to Jira without an explicit `--apply`.
- **Idempotent.** Re-running for the same release must create nothing new. Keep the label dedup.
- **Never push firmware to devices automatically.** Human approval is required for that.
- **No secrets in the repo.** Jira credentials come from `JIRA_EMAIL` / `JIRA_API_TOKEN`
  (GitHub Actions secrets locally: env vars). Do not commit `.env` files.
- **Do not bypass bot protection** on vendor sites (Epiphan's docs site returns a JS challenge).
  Use official feeds, email notices or APIs instead.
- Tests use fake clients; do not make tests call the real Jira API.
- Keep adapters (future) behind the common `Release` model so the pipeline stays vendor-agnostic.

## Workflow
- `main` is protected: work on a branch, open a PR, CI must pass, one approval required.
- Reference the Jira ticket (RECORD-xxx) in branch name or PR description.
- Keep PRs small and focused. Update this file when conventions change.
