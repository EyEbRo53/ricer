"""
Template Manager
----------------
Records confirmed changes in execution order and persists them as
reusable templates in the SQLite database.

Only confirmed-and-verified changes are appended.  Skipped, failed,
and aborted changes never reach this manager.
"""

from __future__ import annotations

import json
import uuid
import sqlite3
from datetime import datetime, timezone


class TemplateManager:
    """CRUD interface for reusable change templates."""

    def __init__(self, db: sqlite3.Connection, session_id: str) -> None:
        self._db = db
        self._session_id = session_id
        self._changes: list[dict] = []

    # ── Building the current template ────────────────────────────────

    def append(self, change: dict) -> None:
        """Add a confirmed change to the session's in-progress template."""
        self._changes.append(change)

    def save(self) -> str:
        """Persist the current session's changes as a template.

        Returns:
            The newly created ``template_id``.
        """
        template_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc).isoformat()

        self._db.execute(
            "INSERT INTO templates (template_id, session_id, name, created_at) "
            "VALUES (?, ?, ?, ?)",
            (template_id, self._session_id, None, now),
        )

        for i, change in enumerate(self._changes, start=1):
            self._db.execute(
                "INSERT INTO template_changes "
                "(template_id, change_order, script, parameters, change_type) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    template_id,
                    i,
                    change.get("script", ""),
                    json.dumps(change.get("parameters", {})),
                    change.get("change_type", ""),
                ),
            )

        self._db.commit()
        return template_id

    # ── Reading templates ────────────────────────────────────────────

    def load(self, template_id: str) -> list[dict]:
        """Load a template's ordered change list."""
        rows = self._db.execute(
            "SELECT change_order, script, parameters, change_type "
            "FROM template_changes WHERE template_id = ? "
            "ORDER BY change_order",
            (template_id,),
        ).fetchall()

        return [
            {
                "order": row[0],
                "script": row[1],
                "parameters": json.loads(row[2]),
                "change_type": row[3],
            }
            for row in rows
        ]

    def list_all(self) -> list[dict]:
        """Return metadata for every saved template (newest first)."""
        rows = self._db.execute(
            "SELECT template_id, session_id, name, created_at "
            "FROM templates ORDER BY created_at DESC"
        ).fetchall()

        return [
            {
                "template_id": row[0],
                "session_id": row[1],
                "name": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    # ── Mutations ────────────────────────────────────────────────────

    def rename(self, template_id: str, name: str) -> None:
        """Give a template a human-readable name."""
        self._db.execute(
            "UPDATE templates SET name = ? WHERE template_id = ?",
            (name, template_id),
        )
        self._db.commit()

    def delete(self, template_id: str) -> None:
        """Delete a template and all its changes."""
        self._db.execute(
            "DELETE FROM template_changes WHERE template_id = ?",
            (template_id,),
        )
        self._db.execute(
            "DELETE FROM templates WHERE template_id = ?",
            (template_id,),
        )
        self._db.commit()
