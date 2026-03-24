"""
MCP System Provider
-------------------
Concrete implementation of the `SystemProvider` interface for `system-utils`.

Connects the generic system utilities (which manage transactions and changes) to
the specific Desktop Environment (e.g. KDE Plasma 6, Cinnamon) via dynamically
loaded `features/` modules in the active provider.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from typing import Any

from provider_runtime import ensure_provider_paths, get_provider_name


class McpSystemProvider:
    """Implements SystemProvider for dynamic UI environments."""

    def __init__(self) -> None:
        _PATHS = ensure_provider_paths()
        self._mcp_root = _PATHS["mcp_root"]
        self._features_dir = _PATHS["features_dir"]
        self._provider_name = get_provider_name()

    # ── Feature module resolution ────────────────────────────────────

    def _module_name_for_script(self, script_name: str) -> str:
        """Map a script function name to its feature module name."""
        if script_name == "move_panel":
            return "panel_position"
        if script_name.startswith("set_"):
            return script_name[4:]
        return script_name

    def _resolve_script_module(self, script_name: str):
        """Resolve and import the module that contains a feature instance."""
        module_name = self._module_name_for_script(script_name)

        if self._features_dir not in sys.path:
            sys.path.insert(0, self._features_dir)

        # Add nested feature directories to sys.path so modules like
        # 'input/cursor_size.py' are importable by name 'cursor_size'.
        for root, dirs, files in os.walk(self._features_dir):
            if root not in sys.path:
                sys.path.insert(0, root)

        module = None

        # Fast path: module may be in a nested folder that is now on sys.path.
        try:
            module = importlib.import_module(module_name)
        except (ModuleNotFoundError, ImportError):
            module = None

        if module is None:
            direct_module_path = os.path.join(self._features_dir, f"{module_name}.py")
            if os.path.exists(direct_module_path):
                for candidate in (f"features.{module_name}", module_name):
                    try:
                        module = importlib.import_module(candidate)
                        break
                    except (ModuleNotFoundError, ImportError):
                        continue

        if module is None:
            if not os.path.isdir(self._features_dir):
                print(f"  ❌ Provider features directory not found: {self._features_dir}")
                return None

            for file_name in os.listdir(self._features_dir):
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
            print(f"  ❌ Could not resolve module for script '{script_name}' in '{self._features_dir}'")
            return None

        return module

    def _state_from_getter_payload(self, payload: dict, parameters: dict) -> dict:
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

    # ── SystemProvider implementation ─────────────────────────────────

    def execute_script(self, script_name: str, parameters: dict[str, Any]) -> bool:
        """Dynamically resolve and call feature.set(...) by script name."""
        module = self._resolve_script_module(script_name)
        if module is None:
            return False

        feature = getattr(module, "feature", None)
        if feature is None:
            print(f"  ⚠️  No module-level 'feature' instance in resolved module for '{script_name}'")
            return False

        setter = getattr(feature, "set", None)
        if not callable(setter):
            print(f"  ⚠️  Feature in resolved module for '{script_name}' has no callable set(...)")
            return False

        try:
            result = setter(**parameters)
            # Most scripts return bool; treat None as success
            return result if result is not None else True
        except Exception as exc:
            print(f"  ❌ Error running {script_name}: {exc}")
            return False

    def read_state(self, script_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Read current script state via feature.get(...)."""
        module = self._resolve_script_module(script_name)
        if module is None:
            return {}

        feature = getattr(module, "feature", None)
        getter = getattr(feature, "get", None) if feature is not None else None
        if not callable(getter):
            print(f"  ⚠️  Feature getter not found for script '{script_name}'")
            return {}

        try:
            payload = getter()
            if isinstance(payload, str):
                payload = json.loads(payload)
            if not isinstance(payload, dict):
                return {}
            return self._state_from_getter_payload(payload, parameters)
        except Exception as exc:
            print(f"  ❌ Error reading state for {script_name}: {exc}")
            return {}

    def post_apply_input_change(self, change: dict[str, Any]) -> None:
        """Handle post-apply actions based on the active UI environment."""
        try:
            if self._provider_name == "kde-plasma-6":
                print("[McpSystemProvider] Restarting plasmashell after input-type change...")
                subprocess.Popen(["plasmashell", "--replace"])
            elif self._provider_name == "cinnamon":
                # Cinnamon example, can be adjusted
                subprocess.Popen(["cinnamon", "--replace"])
            else:
                print(f"[McpSystemProvider] Shell restart not implemented for {self._provider_name}")
        except Exception as e:
            print(f"[McpSystemProvider] Failed to restart shell: {e}")
