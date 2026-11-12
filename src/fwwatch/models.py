"""Common data model shared by all vendor adapters."""
from __future__ import annotations

import re
from dataclasses import dataclass


def slug(text: str) -> str:
    """Lowercase, Jira-label-safe slug (labels cannot contain spaces)."""
    return re.sub(r"[^a-z0-9.\-]+", "-", text.lower()).strip("-")


@dataclass(frozen=True)
class Release:
    vendor: str
    model: str
    version: str
    notes_url: str = ""
    date: str = ""
    source: str = "manual"

    @property
    def label(self) -> str:
        """Stable dedup key, stored as a Jira label on the parent ticket."""
        return "fw-" + slug(f"{self.vendor}-{self.model}-{self.version}")

    @property
    def summary(self) -> str:
        return f"Firmware {self.vendor} {self.model} {self.version}"
