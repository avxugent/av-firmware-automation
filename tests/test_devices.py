import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fwwatch.devices import classify, parse_version  # noqa: E402


class VersionTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_version("v4.24.4-beta"), (4, 24, 4))
        self.assertIsNone(parse_version("unknown"))
        self.assertIsNone(parse_version(None))


class ClassifyTests(unittest.TestCase):
    DEVICES = [
        {"name": "a", "model": "Pearl-2", "firmware": "4.23.1"},
        {"name": "b", "model": "pearl-2", "firmware": "4.24.4"},
        {"name": "c", "model": "Pearl-2", "firmware": "4.24"},
        {"name": "d", "model": "Pearl-2", "firmware": ""},
        {"name": "e", "model": "Pearl Mini", "firmware": "1.0.0"},
        {"name": "f", "model": "Pearl-2", "firmware": "4.100.0"},
    ]

    def test_split(self):
        needs, unknown, current = classify(self.DEVICES, "Pearl-2", "4.24.4")
        self.assertEqual([d["name"] for d in needs], ["a", "c"])
        self.assertEqual([d["name"] for d in unknown], ["d"])
        self.assertEqual([d["name"] for d in current], ["b", "f"])

    def test_other_models_ignored(self):
        needs, unknown, current = classify(self.DEVICES, "Pearl Mini", "2.0.0")
        self.assertEqual([d["name"] for d in needs], ["e"])
        self.assertEqual(unknown + current, [])

    def test_bad_target_raises(self):
        with self.assertRaises(ValueError):
            classify(self.DEVICES, "Pearl-2", "latest")


if __name__ == "__main__":
    unittest.main()
