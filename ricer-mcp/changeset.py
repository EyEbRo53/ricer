"""
Changeset Manager
-----------------
In-memory staging area for desktop changes. Tools add entries here;
nothing executes until confirm_change() is called by the control layer.

The changeset is intentionally ephemeral — it lives in memory and is
lost if the server restarts. Confirmed changes survive because they
are written to disk by the scripts themselves.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ChangeEntry:
    """A single staged change in the changeset."""

    order: int
    status: str  # "staged", "applied", "skipped"
    description: str
    change_type: str  # "input" or "display"
    script: str
    parameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class Changeset:
    """Manages the in-memory list of staged changes."""

    def __init__(self) -> None:
        self._changes: list[ChangeEntry] = []
        self._counter: int = 0

    # ── Staging ──────────────────────────────────────────────────────

    def add(
        self,
        description: str,
        change_type: str,
        script: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Stage a new change and return its receipt.

        Returns:
            The order object dict (status="staged").
        """
        self._counter += 1
        entry = ChangeEntry(
            order=self._counter,
            status="staged",
            description=description,
            change_type=change_type,
            script=script,
            parameters=parameters,
        )
        self._changes.append(entry)
        return entry.to_dict()

    # ── Querying ─────────────────────────────────────────────────────

    def get(self, order: int) -> ChangeEntry | None:
        """Look up a change by its order number."""
        for entry in self._changes:
            if entry.order == order:
                return entry
        return None

    def all(self) -> list[dict[str, Any]]:
        """Return all entries as dicts (for review_changeset)."""
        return [e.to_dict() for e in self._changes]

    def staged(self) -> list[ChangeEntry]:
        """Return only entries still in 'staged' status."""
        return [e for e in self._changes if e.status == "staged"]

    @property
    def size(self) -> int:
        return len(self._changes)

    @property
    def is_empty(self) -> bool:
        return len(self._changes) == 0

    # ── Lifecycle transitions ────────────────────────────────────────

    def mark_applied(self, order: int) -> ChangeEntry | None:
        entry = self.get(order)
        if entry and entry.status == "staged":
            entry.status = "applied"
        return entry

    def mark_skipped(self, order: int) -> ChangeEntry | None:
        entry = self.get(order)
        if entry and entry.status == "staged":
            entry.status = "skipped"
        return entry

    def skip_all_remaining(self) -> int:
        """Mark all staged entries as skipped. Returns count skipped."""
        count = 0
        for entry in self._changes:
            if entry.status == "staged":
                entry.status = "skipped"
                count += 1
        return count

    # ── Reset ────────────────────────────────────────────────────────

    def clear(self) -> None:
        """Discard everything and reset the counter."""
        self._changes.clear()
        self._counter = 0


# ── Module-level singleton ───────────────────────────────────────────
changeset = Changeset()
