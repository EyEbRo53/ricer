"""
Session Handler
---------------
Lifecycle owner for a single MCP session.

Creates one instance of every utility, wires them together via
callbacks, and owns the SQLite database connection.

Usage::

    provider = McpSystemProvider()
    session = SessionHandler(provider)
    result  = session.confirm_change(receipt_dict)
    session.close()
"""

from __future__ import annotations

import os
import uuid
import sqlite3
from datetime import datetime, timezone

from config_checker import ConfigChecker
from state_manager import StateManager
from template_manager import TemplateManager
from failure_handler import FailureHandler
from order_manager import OrderManager
from provider_interface import SystemProvider

_DB_DIR = os.path.expanduser("~/.config/ricer")
_DB_PATH = os.path.join(_DB_DIR, "ricer.db")

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS sessions (
    session_id   TEXT PRIMARY KEY,
    created_at   TEXT NOT NULL,
    closed_at    TEXT
);

CREATE TABLE IF NOT EXISTS snapshots (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT NOT NULL REFERENCES sessions(session_id),
    config_key   TEXT NOT NULL,
    value        TEXT NOT NULL,
    captured_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deltas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT NOT NULL REFERENCES sessions(session_id),
    change_order INTEGER NOT NULL,
    config_key   TEXT NOT NULL,
    before_value TEXT NOT NULL,
    after_value  TEXT NOT NULL,
    applied_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS templates (
    template_id  TEXT PRIMARY KEY,
    session_id   TEXT REFERENCES sessions(session_id),
    name         TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS template_changes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id  TEXT NOT NULL REFERENCES templates(template_id),
    change_order INTEGER NOT NULL,
    script       TEXT NOT NULL,
    parameters   TEXT NOT NULL,
    change_type  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS failures (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT NOT NULL REFERENCES sessions(session_id),
    script       TEXT NOT NULL,
    parameters   TEXT NOT NULL,
    error_type   TEXT NOT NULL,
    detail       TEXT,
    logged_at    TEXT NOT NULL
);
"""


class SessionHandler:
    """One-per-session container that owns and wires all utilities."""

    def __init__(self, provider: SystemProvider) -> None:
        self._provider = provider
        self._session_id = uuid.uuid4().hex[:8]
        self._db = self._init_db()
        self._record_session()

        # ── Create utilities ─────────────────────────────────────────
        self.config_checker = ConfigChecker()
        self.state_manager = StateManager(
            self._db,
            self._session_id,
            on_execute=self._provider.execute_script,
            on_reverse_params=self._reverse_params,
        )
        self.template_manager = TemplateManager(self._db, self._session_id)
        self.failure_handler = FailureHandler()

        # ── Wire order manager via callbacks ─────────────────────────
        self.order_manager = OrderManager(
            on_snapshot=self._snapshot,
            on_verify=self._verify,
            on_success=self._on_success,
            on_failure=self._on_failure,
            on_execute=self._provider.execute_script,
            post_apply=self._provider.post_apply_input_change,
        )

    # ── Callback wiring (private) ────────────────────────────────────

    def _snapshot(self, change: dict) -> dict:
        """Read current config values for the keys this change touches."""
        return self._provider.read_state(
            change["script"], change["parameters"]
        )

    def _verify(self, change: dict, before: dict, after: dict) -> bool:
        """Check whether the config now matches the expected values."""
        return self.config_checker.verify(
            before, after, change["parameters"]
        )

    def _on_success(self, change: dict, before: dict, after: dict) -> None:
        """Record the delta and append to the template."""
        self.state_manager.record(change, before, after)
        self.template_manager.append(change)

    def _on_failure(self, change: dict, error_type: str, detail: str) -> None:
        """Log the failure."""
        self.failure_handler.log(change, error_type, detail)

    def _reverse_params(self, script: str, snapshot: dict) -> dict:
        """Convert config snapshot → script parameters — used by State Manager."""
        _ = script
        return self.config_checker.reverse_parameters(snapshot)

    # ── Public interface ─────────────────────────────────────────────

    def confirm_change(self, change: dict) -> dict:
        """Execute and verify a single confirmed change.

        Args:
            change: A receipt dict (order, script, parameters, …).

        Returns:
            ``{"status": "applied"}`` or ``{"status": "failed", "error": …}``.
        """
        return self.order_manager.execute(change)

    def undo(self) -> dict:
        """Undo the most recent confirmed change.

        Delegates to State Manager, which restores the 'before' values
        via the injected on_execute / on_reverse_params callbacks.
        """
        return self.state_manager.undo()

    def redo(self) -> dict:
        """Redo the most recently undone change.

        Delegates to State Manager, which re-applies the original
        parameters via the injected on_execute callback.
        """
        return self.state_manager.redo()

    def save_template(self) -> str:
        """Persist all confirmed changes as a reusable template."""
        return self.template_manager.save()

    @property
    def session_id(self) -> str:
        return self._session_id

    # ── Lifecycle ────────────────────────────────────────────────────

    def close(self) -> None:
        """Mark the session as closed and release the database."""
        now = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "UPDATE sessions SET closed_at = ? WHERE session_id = ?",
            (now, self._session_id),
        )
        self._db.commit()
        self._db.close()

    # ── Database bootstrap ───────────────────────────────────────────

    @staticmethod
    def _init_db() -> sqlite3.Connection:
        os.makedirs(_DB_DIR, exist_ok=True)
        db = sqlite3.connect(_DB_PATH, check_same_thread=False)
        db.executescript(_SCHEMA)
        return db

    def _record_session(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "INSERT INTO sessions (session_id, created_at) VALUES (?, ?)",
            (self._session_id, now),
        )
        self._db.commit()
