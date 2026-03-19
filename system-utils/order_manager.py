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

_RICER_MCP_DIR = os.path.join(os.path.dirname(__file__), "..", "ricer-mcp")
_FEATURES_DIR = os.path.join(_RICER_MCP_DIR, "features")


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
        """Dynamically resolve and call a feature function by script name."""
        func_name = script_name

        # Add package roots to support imports from feature modules plus
        # their utility dependencies.
        if _FEATURES_DIR not in sys.path:
            sys.path.insert(0, _FEATURES_DIR)
        if _RICER_MCP_DIR not in sys.path:
            sys.path.insert(0, _RICER_MCP_DIR)

        # First try direct module lookup (legacy behavior).
        module = None
        module_name = None

        direct_module_path = os.path.join(_FEATURES_DIR, f"{script_name}.py")
        if os.path.exists(direct_module_path):
            for candidate in (f"features.{script_name}", script_name):
                try:
                    module = importlib.import_module(candidate)
                    module_name = candidate
                    break
                except (ModuleNotFoundError, ImportError):
                    continue

        # Fallback: locate the callable in any feature module.
        if module is None:
            for file_name in os.listdir(_FEATURES_DIR):
                if not file_name.endswith(".py") or file_name.startswith("__"):
                    continue

                candidate_mod = file_name[:-3]
                for candidate in (f"features.{candidate_mod}", candidate_mod):
                    try:
                        scanned_module = importlib.import_module(candidate)
                    except (ModuleNotFoundError, ImportError):
                        continue

                    if hasattr(scanned_module, func_name):
                        module = scanned_module
                        module_name = candidate
                        break

                if module is not None:
                    break

        if module is None:
            print(
                f"  ❌ Could not resolve script '{script_name}' in /ricer-mcp/features/"
            )
            return False

        if not hasattr(module, func_name):
            print(f"  ⚠️  No callable '{func_name}' in {module_name}.py — "
                  f"cannot execute")
            return False

        try:
            result = getattr(module, func_name)(**parameters)
            # Most scripts return bool; treat None as success
            return result if result is not None else True
        except Exception as exc:
            print(f"  ❌ Error running {script_name}: {exc}")
            return False
