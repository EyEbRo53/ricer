"""
Failure Handler (Dummy)
-----------------------
Placeholder — logs failures in memory only.
Full persistence to SQLite will be added later.
"""

from __future__ import annotations


class FailureHandler:
    """Collects execution failures in memory for later inspection."""

    def __init__(self) -> None:
        self._failures: list[dict] = []

    def log(self, change: dict, error_type: str, detail: str) -> None:
        """Record a failure.

        Args:
            change:     The ChangeEntry dict that failed.
            error_type: "verification_failed" | "script_error" | "retry_exhausted"
            detail:     Human-readable explanation.
        """
        self._failures.append(
            {
                "script": change.get("script"),
                "parameters": change.get("parameters"),
                "error_type": error_type,
                "detail": detail,
            }
        )

    def get_failures(self) -> list[dict]:
        """Return all recorded failures (copies)."""
        return list(self._failures)
