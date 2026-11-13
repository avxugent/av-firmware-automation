"""Pick the devices that need a firmware update (pure logic, no network)."""

from __future__ import annotations

import re


def parse_version(text: str | None) -> tuple[int, ...] | None:
    """First dotted number in the text, e.g. 'v4.24.4-beta' -> (4, 24, 4). None if absent."""
    match = re.search(r"\d+(?:\.\d+)*", text or "")
    return tuple(int(part) for part in match.group().split(".")) if match else None


def _less(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    width = max(len(a), len(b))
    pad = lambda v: v + (0,) * (width - len(v))  # noqa: E731
    return pad(a) < pad(b)


def classify(devices: list[dict], model: str, target: str) -> tuple[list, list, list]:
    """Split devices of `model` into (needs_update, unknown_version, up_to_date).

    Each device is a dict with at least `model` and `firmware`. Devices of other models are
    ignored. Devices whose firmware cannot be parsed go to `unknown_version` for human review.
    """
    target_version = parse_version(target)
    if target_version is None:
        raise ValueError(f"Cannot parse target version: {target!r}")

    needs, unknown, current = [], [], []
    for device in devices:
        if str(device.get("model", "")).strip().lower() != model.strip().lower():
            continue
        version = parse_version(device.get("firmware"))
        if version is None:
            unknown.append(device)
        elif _less(version, target_version):
            needs.append(device)
        else:
            current.append(device)
    return needs, unknown, current
