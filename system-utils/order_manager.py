"""
Order Manager
-------------
Executes a single confirmed change.  Stateless between calls.

Uses five injected callbacks — has **zero** imports from sibling
utilities.  The Session Handler wires the callbacks at creation time.

Execution flow for one change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Snapshot current value        → on_snapshot(change) → before dict
2. Run the script                → on_execute(script, params)
3. Verify the config took effect → on_verify(change) → bool
4. If verified                   → on_success(change, before, after)
5. If verification failed        → retry once, then on_failure(…)
"""

from __future__ import annotations

from typing import Any, Callable


class OrderManager:
    """Executes confirmed changes through injected callbacks."""

    def __init__(
        self,
        on_snapshot: Callable[[dict], dict],
        on_verify: Callable[[dict, dict, dict], bool],
        on_success: Callable[[dict, dict, dict], None],
        on_failure: Callable[[dict, str, str], None],
        on_execute: Callable[[str, dict], bool],
        post_apply: Callable[[dict], None] = None,
    ) -> None:
        """Create an OrderManager with injected callbacks.

        Args:
            on_snapshot: Called before/after execution to read current values
                for keys affected by ``change``.
            on_verify: Called after execution to verify values.
            on_success: Called when execution + verification succeed.
            on_failure: Called when execution fails or verification fails.
            on_execute: Called to run the configuration script.
            post_apply: Optional callback called after successful apply for certain change types.
        """
        self._on_snapshot = on_snapshot
        self._on_verify = on_verify
        self._on_success = on_success
        self._on_failure = on_failure
        self._on_execute = on_execute
        self._post_apply = post_apply

    # ── Public interface ─────────────────────────────────────────────

    def execute(self, change: dict) -> dict[str, Any]:
        """Execute a single confirmed change.

        Args:
            change: Dict with keys ``script``, ``parameters``, ``order``,
                    ``change_type``, ``description``.

        Returns:
            ``{"status": "applied"}`` on success, or
            ``{"status": "failed", "error": "<type>"}`` on failure.
        """
        script = change["script"]
        params = change["parameters"]

        # 1. Snapshot current values
        before = self._on_snapshot(change)

        # 2. Execute the script
        success = self._on_execute(script, params)
        if not success:
            self._on_failure(change, "script_error",
                             f"Script '{script}' execution failed")
            return {"status": "failed", "error": "script_error"}

        # 3. Verify
        after = self._on_snapshot(change)
        if self._on_verify(change, before, after):
            self._on_success(change, before, after)
            # Post-apply hook for input-type changes
            if self._post_apply and change.get("change_type") == "input":
                self._post_apply(change)
            return {"status": "applied"}

        # 4. Retry once
        success = self._on_execute(script, params)
        if success:
            after = self._on_snapshot(change)
            if self._on_verify(change, before, after):
                self._on_success(change, before, after)
                if self._post_apply and change.get("change_type") == "input":
                    self._post_apply(change)
                return {"status": "applied"}

        # 5. Failed after retry
        self._on_failure(change, "verification_failed",
                         f"Config not updated after retry for '{script}'")
        return {"status": "failed", "error": "verification_failed"}
