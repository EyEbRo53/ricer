"""
Order Manager
-------------
Executes a single confirmed change.  Stateless between calls.

Uses four injected callbacks — has **zero** imports from sibling
utilities.  The Session Handler wires the callbacks at creation time.

Execution flow for one change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Snapshot current value        → on_snapshot(change) → before dict
2. Run the script                → import + call from /scripts/
3. Verify the config took effect → on_verify(change) → bool
4. If verified                   → on_success(change, before, after)
5. If verification failed        → retry once, then on_failure(…)
"""

from __future__ import annotations

import importlib
import sys
import os
from typing import Any, Callable

_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")


class OrderManager:
    """Executes confirmed changes through injected callbacks."""

    def __init__(
        self,
        on_snapshot: Callable[[dict], dict],
        on_verify: Callable[[dict], bool],
        on_success: Callable[[dict, dict, dict], None],
        on_failure: Callable[[dict, str, str], None],
    ) -> None:
        """Create an OrderManager with injected callbacks.

        Args:
            on_snapshot: Called before/after execution to read current values
                for keys affected by ``change``.
                Signature: ``on_snapshot(change) -> dict``.

            on_verify: Called after execution to verify that expected values
                were applied.
                Signature: ``on_verify(change) -> bool``.

            on_success: Called when execution + verification succeed.
                Receives the original ``change`` and its ``before``/``after``
                snapshots so higher-level utilities can record deltas and
                append templates.
                Signature: ``on_success(change, before, after) -> None``.

            on_failure: Called when execution fails or verification fails
                after retry.
                Signature:
                ``on_failure(change, error_type, detail) -> None``.
        """
        self._on_snapshot = on_snapshot
        self._on_verify = on_verify
        self._on_success = on_success
        self._on_failure = on_failure

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
        success = self._run_script(script, params)
        if not success:
            self._on_failure(change, "script_error",
                             f"Script '{script}' execution failed")
            return {"status": "failed", "error": "script_error"}

        # 3. Verify
        if self._on_verify(change):
            after = self._on_snapshot(change)
            self._on_success(change, before, after)
            return {"status": "applied"}

        # 4. Retry once
        success = self._run_script(script, params)
        if success and self._on_verify(change):
            after = self._on_snapshot(change)
            self._on_success(change, before, after)
            return {"status": "applied"}

        # 5. Failed after retry
        self._on_failure(change, "verification_failed",
                         f"Config not updated after retry for '{script}'")
        return {"status": "failed", "error": "verification_failed"}

    # ── Script execution ─────────────────────────────────────────────

    @staticmethod
    def _run_script(script_name: str, parameters: dict) -> bool:
        """Dynamically import a script from /scripts/ and call its function."""
        func_name = script_name

        if _SCRIPTS_DIR not in sys.path:
            sys.path.insert(0, _SCRIPTS_DIR)

        try:
            module = importlib.import_module(script_name)
        except ModuleNotFoundError:
            print(f"  ❌ Script module '{script_name}' not found in /scripts/")
            return False

        if not hasattr(module, func_name):
            print(f"  ⚠️  No callable '{func_name}' in {script_name}.py — "
                  f"cannot execute")
            return False

        try:
            result = getattr(module, func_name)(**parameters)
            # Most scripts return bool; treat None as success
            return result if result is not None else True
        except Exception as exc:
            print(f"  ❌ Error running {script_name}: {exc}")
            return False
