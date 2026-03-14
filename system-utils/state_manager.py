"""
State Manager
-------------
Tracks configuration state for undo / redo support.

Each confirmed change is stored as a *delta* (before → after values).
Deltas are pushed onto an undo stack; undoing pops them to a redo stack.
Any new change clears the redo stack (same semantics as a text editor).

Deltas are also persisted to the ``deltas`` table in SQLite so they
survive across sessions.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any, Callable


class StateManager:
    """Manages per-change deltas and undo / redo stacks."""

    def __init__(
        self,
        db: sqlite3.Connection,
        session_id: str,
        on_execute: Callable[[str, dict], bool] | None = None,
        on_reverse_params: Callable[[str, dict], dict] | None = None,
    ) -> None:
        """
        Args:
            db: SQLite connection for persisting deltas.
            session_id: Current session identifier.
            on_execute: Runs a script by name with the given parameters.
                Signature: ``on_execute(script, parameters) -> bool``.
            on_reverse_params: Converts a config snapshot dict back to
                the parameter dict the script expects.
                Signature: ``on_reverse_params(script, snapshot) -> dict``.
        """
        self._db = db
        self._session_id = session_id
        self._on_execute = on_execute
        self._on_reverse_params = on_reverse_params
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []

    # ── Recording ────────────────────────────────────────────────────

    def record(self, change: dict, before: dict, after: dict) -> None:
        """Record a verified delta and push it onto the undo stack.

        Args:
            change: The ChangeEntry dict (must contain at least ``order``).
            before: ``{config_key: value}`` *before* execution.
            after:  ``{config_key: value}`` *after* execution.
        """
        delta = {"change": change, "before": before, "after": after}
        self._undo_stack.append(delta)
        self._redo_stack.clear()

        # Persist
        now = datetime.now(timezone.utc).isoformat()
        order = change.get("order", len(self._undo_stack))
        for config_key in before:
            self._db.execute(
                """INSERT INTO deltas
                   (session_id, change_order, config_key,
                    before_value, after_value, applied_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    self._session_id,
                    order,
                    config_key,
                    str(before.get(config_key, "")),
                    str(after.get(config_key, "")),
                    now,
                ),
            )
        self._db.commit()

    # ── Undo / Redo ─────────────────────────────────────────────────

    def peek_undo(self) -> dict | None:
        """Return the top delta on the undo stack *without* popping it."""
        return self._undo_stack[-1] if self._undo_stack else None

    def peek_redo(self) -> dict | None:
        """Return the top delta on the redo stack *without* popping it."""
        return self._redo_stack[-1] if self._redo_stack else None

    def undo(self) -> dict:
        """Revert the most recent confirmed change.

        Peeks at the top of the undo stack, builds reverse parameters
        from the *before* snapshot, executes the script to restore
        the previous values, and only then commits the stack move.

        Returns:
            ``{"status": "undone", "change": …}`` on success,
            ``{"status": "nothing_to_undo"}`` if stack is empty,
            ``{"status": "unsupported", "error": …}`` for scripts
            whose config snapshots are empty (DBus / kscreen-doctor),
            ``{"status": "failed", "error": …}`` on execution failure.
        """
        delta = self.peek_undo()
        if delta is None:
            return {"status": "nothing_to_undo"}

        change = delta["change"]
        before = delta["before"]
        script = change["script"]

        # Build parameters that restore the 'before' state
        reverse_params = self._on_reverse_params(script, before)
        if not reverse_params:
            return {
                "status": "unsupported",
                "error": (
                    f"Cannot undo '{script}' — no config snapshot available"
                ),
            }

        # Execute the reversal script
        success = self._on_execute(script, reverse_params)
        if not success:
            return {
                "status": "failed",
                "error": f"Script '{script}' reversal failed",
            }

        # Script succeeded — commit the stack move
        self._undo_stack.pop()
        self._redo_stack.append(delta)
        return {"status": "undone", "change": change}

    def redo(self) -> dict:
        """Re-apply the most recently undone change.

        Peeks at the top of the redo stack, re-executes the original
        script with its original parameters, and only then commits
        the stack move.

        Returns:
            ``{"status": "reapplied", "change": …}`` on success,
            ``{"status": "nothing_to_redo"}`` if stack is empty,
            ``{"status": "failed", "error": …}`` on execution failure.
        """
        delta = self.peek_redo()
        if delta is None:
            return {"status": "nothing_to_redo"}

        change = delta["change"]
        script = change["script"]
        params = change["parameters"]

        # Re-execute the original change
        success = self._on_execute(script, params)
        if not success:
            return {
                "status": "failed",
                "error": f"Script '{script}' re-execution failed",
            }

        # Script succeeded — commit the stack move
        self._redo_stack.pop()
        self._undo_stack.append(delta)
        return {"status": "reapplied", "change": change}

    # ── Introspection ────────────────────────────────────────────────

    def get_undo_stack(self) -> list[dict]:
        return list(self._undo_stack)

    def get_redo_stack(self) -> list[dict]:
        return list(self._redo_stack)

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0
