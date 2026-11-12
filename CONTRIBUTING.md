# Contributing

1. Branch from `main`: `git switch -c RECORD-123-short-description`.
2. Make your change; add or update tests.
3. Run the checks locally (same as CI):
   ```bash
   pip install -r requirements.txt ruff
   ruff format . && ruff check .
   python -m unittest discover -s tests
   ```
4. Open a PR using the template. CI must be green and one teammate must approve.
5. Squash-merge into `main`.

Testing against the real Jira: run the `firmware-watch` workflow with a throwaway version such as
`0.0.0-test` (dry run first), then delete the test tickets in `RECORD`.

Conventions for AI-assisted work are in [CLAUDE.md](CLAUDE.md).
