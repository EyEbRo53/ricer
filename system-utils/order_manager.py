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
import json
import sys
import os
from typing import Any, Callable

_RICER_MCP_DIR = os.path.join(os.path.dirname(__file__), "..", "ricer-mcp")
if _RICER_MCP_DIR not in sys.path:
    sys.path.insert(0, _RICER_MCP_DIR)

from provider_runtime import ensure_provider_paths

_PATHS = ensure_provider_paths(_RICER_MCP_DIR)
_FEATURES_DIR = _PATHS["features_dir"]


class OrderManager:
    """Executes confirmed changes through injected callbacks."""

    def __init__(
        self,
        on_snapshot: Callable[[dict], dict],
        on_verify: Callable[[dict, dict, dict], bool],
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
                Signature: ``on_verify(change, before, after) -> bool``.

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
        after = self._on_snapshot(change)
        if self._on_verify(change, before, after):
            self._on_success(change, before, after)
            return {"status": "applied"}

        # 4. Retry once
        success = self._run_script(script, params)
        if success:
            after = self._on_snapshot(change)
            if self._on_verify(change, before, after):
                self._on_success(change, before, after)
                return {"status": "applied"}

        # 5. Failed after retry
        self._on_failure(change, "verification_failed",
                         f"Config not updated after retry for '{script}'")
        return {"status": "failed", "error": "verification_failed"}

    # ── Script execution ─────────────────────────────────────────────

    @staticmethod
    def _module_name_for_script(script_name: str) -> str:
        """Map a script function name to its feature module name."""
        if script_name == "move_panel":
            return "panel_position"
        if script_name.startswith("set_"):
            return script_name[4:]
        return script_name

    @staticmethod
    def _resolve_script_module(script_name: str):
        """Resolve and import the module that contains a feature instance."""
        module_name = OrderManager._module_name_for_script(script_name)

        ensure_provider_paths(_RICER_MCP_DIR)
        if _FEATURES_DIR not in sys.path:
            sys.path.insert(0, _FEATURES_DIR)

        module = None
        direct_module_path = os.path.join(_FEATURES_DIR, f"{module_name}.py")
        if os.path.exists(direct_module_path):
            for candidate in (f"features.{module_name}", module_name):
                try:
                    module = importlib.import_module(candidate)
                    break
                except (ModuleNotFoundError, ImportError):
                    continue

        if module is None:
            if not os.path.isdir(_FEATURES_DIR):
                print(
                    f"  ❌ Provider features directory not found: {_FEATURES_DIR}"
                )
                return None

            for file_name in os.listdir(_FEATURES_DIR):
                if not file_name.endswith(".py") or file_name.startswith("__"):
                    continue

                candidate_mod = file_name[:-3]
                for candidate in (f"features.{candidate_mod}", candidate_mod):
                    try:
                        scanned_module = importlib.import_module(candidate)
                    except (ModuleNotFoundError, ImportError):
                        continue

                    if candidate_mod == module_name:
                        module = scanned_module
                        break

                if module is not None:
                    break

        if module is None:
            print(
                f"  ❌ Could not resolve module for script '{script_name}' in '{_FEATURES_DIR}'"
            )
            return None

        return module

    @staticmethod
    def _run_script(script_name: str, parameters: dict) -> bool:
        """Dynamically resolve and call feature.set(...) by script name."""
        module = OrderManager._resolve_script_module(script_name)
        if module is None:
            return False

        feature = getattr(module, "feature", None)
        if feature is None:
            print(
                f"  ⚠️  No module-level 'feature' instance in resolved module for '{script_name}'"
            )
            return False

        setter = getattr(feature, "set", None)
        if not callable(setter):
            print(
                f"  ⚠️  Feature in resolved module for '{script_name}' has no callable set(...)"
            )
            return False

        try:
            result = setter(**parameters)
            # Most scripts return bool; treat None as success
            return result if result is not None else True
        except Exception as exc:
            print(f"  ❌ Error running {script_name}: {exc}")
            return False

    @staticmethod
    def read_state(script_name: str, parameters: dict) -> dict:
        """Read current script state via feature.get(...)."""
        module = OrderManager._resolve_script_module(script_name)
        if module is None:
            return {}

        feature = getattr(module, "feature", None)
        getter = getattr(feature, "get", None) if feature is not None else None
        if not callable(getter):
            print(
                f"  ⚠️  Feature getter not found for script '{script_name}'"
            )
            return {}

        try:
            payload = getter()
            if isinstance(payload, str):
                payload = json.loads(payload)
            if not isinstance(payload, dict):
                return {}
            return OrderManager._state_from_getter_payload(payload, parameters)
        except Exception as exc:
            print(f"  ❌ Error reading state for {script_name}: {exc}")
            return {}

    @staticmethod
    def _state_from_getter_payload(payload: dict, parameters: dict) -> dict:
        """Extract comparable state from a resource getter payload."""
        if payload.get("error"):
            return {}

        values = payload.get("values")
        if isinstance(values, dict):
            return values

        if "enabled" in parameters and "enabled" in payload:
            return {"enabled": payload.get("enabled")}

        if "value" in payload and parameters:
            key = next(iter(parameters.keys()))
            return {key: payload.get("value")}

        return {}
