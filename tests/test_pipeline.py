import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fwwatch.models import Release  # noqa: E402
from fwwatch.pipeline import run  # noqa: E402

CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
TEMPLATE = yaml.safe_load((ROOT / "templates" / "subtasks.yaml").read_text())["subtasks"]
REL = Release("Epiphan", "Pearl-2", "4.24.4", "https://example.com/notes", "2026-11-01")


class FakeClient:
    def __init__(self, existing=None):
        self.existing = existing
        self.created = []

    def find_by_label(self, project, label):
        return self.existing

    def create_issue(self, fields):
        self.created.append(fields)
        return f"RECORD-{len(self.created)}"


class PipelineTests(unittest.TestCase):
    def test_label_is_stable_and_safe(self):
        self.assertEqual(REL.label, "fw-epiphan-pearl-2-4.24.4")

    def test_dry_run_without_client_writes_nothing(self):
        report = run(REL, CFG, TEMPLATE, None, apply=False)
        self.assertEqual(report["status"], "dry-run")
        self.assertEqual(len(report["subtasks"]), len(TEMPLATE))
        self.assertIn(REL.label, report["parent"]["labels"])

    def test_dry_run_with_client_does_not_create(self):
        client = FakeClient()
        report = run(REL, CFG, TEMPLATE, client, apply=False)
        self.assertEqual(report["status"], "dry-run")
        self.assertEqual(client.created, [])

    def test_apply_creates_parent_then_subtasks(self):
        client = FakeClient()
        report = run(REL, CFG, TEMPLATE, client, apply=True)
        self.assertEqual(report["status"], "created")
        self.assertEqual(len(client.created), 1 + len(TEMPLATE))
        self.assertEqual(client.created[1]["parent"]["key"], "RECORD-1")
        self.assertEqual(client.created[1]["issuetype"]["name"], "Sub-task")

    def test_existing_release_is_not_duplicated(self):
        client = FakeClient(existing="RECORD-99")
        report = run(REL, CFG, TEMPLATE, client, apply=True)
        self.assertEqual(report["status"], "exists")
        self.assertEqual(report["parent"], "RECORD-99")
        self.assertEqual(client.created, [])


if __name__ == "__main__":
    unittest.main()
