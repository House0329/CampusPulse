"""Session-only demo pulse helpers. Pure functions — nothing is written to disk."""

from __future__ import annotations

from typing import Any

PULSE_HEADING = "Demo pulse"
PULSE_DISCLAIMER = "Stored only in this browser session; not real campus activity."
PULSE_EMPTY = "No demo pulse submitted in this session."


def make_pulse(
    space_id: str,
    noise: int,
    crowding: int,
    comfort: int,
    would_return: bool,
) -> dict[str, Any]:
    payload = {
        "space_id": str(space_id),
        "noise": int(noise),
        "crowding": int(crowding),
        "comfort": int(comfort),
        "would_return": bool(would_return),
    }
    for key in ("noise", "crowding", "comfort"):
        value = payload[key]
        if value < 1 or value > 5:
            raise ValueError(f"{key} must be between 1 and 5")
    return payload


def append_pulse(entries: list[dict[str, Any]], pulse: dict[str, Any]) -> list[dict[str, Any]]:
    return list(entries) + [pulse]


def pulses_for_space(entries: list[dict[str, Any]], space_id: str) -> list[dict[str, Any]]:
    return [item for item in entries if item.get("space_id") == space_id]
