"""Provider runtime helpers for locating active MCP provider code."""

from __future__ import annotations

import importlib.util
import os
import sys


DEFAULT_PROVIDER = "kde-plasma-6"
PROVIDER_ENV_VAR = "RICER_PROVIDER"

_DE_TO_PROVIDER = {
    "kde plasma": "kde-plasma-6",
    "gnome": "gnome",
    "cinnamon": "cinnamon",
    "xfce": "xfce",
    "mate": "mate",
    "lxqt": "lxqt",
}


def _load_os_details_module(mcp_root: str) -> object | None:
    """Load system-utils/get-os-details.py dynamically."""
    os_details_path = os.path.join(
        os.path.dirname(mcp_root), "system-utils", "get-os-details.py"
    )
    if not os.path.isfile(os_details_path):
        return None

    spec = importlib.util.spec_from_file_location("ricer_get_os_details", os_details_path)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _detect_provider_from_os(mcp_root: str) -> str | None:
    """Detect provider id from current desktop environment."""
    # 1. Primary check: Use environment variables directly (lightweight & robust)
    xdg_current = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
    desktop_session = os.environ.get("DESKTOP_SESSION", "").upper()
    de_marker = f"{xdg_current}:{desktop_session}"

    if "CINNAMON" in de_marker:
        return "cinnamon"
    if "KDE" in de_marker or "PLASMA" in de_marker:
        return "kde-plasma-6"
    if "GNOME" in de_marker:
        return "gnome"
    if "XFCE" in de_marker:
        return "xfce"
    if "MATE" in de_marker:
        return "mate"
    if "LXQT" in de_marker:
        return "lxqt"

    # 2. Secondary check: Fallback to external comprehensive detection script
    module = _load_os_details_module(mcp_root)
    if module is None or not hasattr(module, "get_ui_environment"):
        return None

    try:
        ui_info = module.get_ui_environment()
        de_name = str(ui_info.get("Desktop Environment", "")).strip().lower()
        provider = _DE_TO_PROVIDER.get(de_name)
        if provider:
            return provider
    except Exception:
        pass

    return None


def get_provider_name(mcp_root: str | None = None) -> str:
    """Return provider identifier from env or detected desktop environment."""
    root = mcp_root or os.path.dirname(__file__)

    provider = os.getenv(PROVIDER_ENV_VAR, "").strip()
    if provider:
        return provider

    detected = _detect_provider_from_os(root)
    if detected:
        return detected

    return DEFAULT_PROVIDER


def get_provider_root(mcp_root: str | None = None) -> str:
    """Return absolute path to the active provider directory."""
    root = mcp_root or os.path.dirname(__file__)
    return os.path.join(root, "providers", get_provider_name(root))


def ensure_provider_paths(mcp_root: str | None = None) -> dict[str, str]:
    """Ensure provider and MCP roots are importable via sys.path."""
    root = mcp_root or os.path.dirname(__file__)
    provider_from_env = os.getenv(PROVIDER_ENV_VAR, "").strip()
    provider_detected = _detect_provider_from_os(root)
    provider_name = provider_from_env or provider_detected or DEFAULT_PROVIDER
    provider_root = os.path.join(root, "providers", provider_name)

    if not os.path.isdir(provider_root):
        if provider_from_env:
            raise RuntimeError(
                f"Provider '{provider_name}' from {PROVIDER_ENV_VAR} not found at "
                f"'{provider_root}'."
            )

        if provider_detected and provider_detected != DEFAULT_PROVIDER:
            raise RuntimeError(
                f"Detected desktop provider '{provider_detected}', but no matching "
                f"provider directory exists at '{provider_root}'. Refusing to "
                f"fallback to '{DEFAULT_PROVIDER}' automatically."
            )

        fallback_root = os.path.join(root, "providers", DEFAULT_PROVIDER)
        if os.path.isdir(fallback_root):
            print(
                f"[ricer-mcp] Provider '{provider_name}' not found. "
                f"Falling back to '{DEFAULT_PROVIDER}'."
            )
            provider_root = fallback_root
            provider_name = DEFAULT_PROVIDER
        else:
            raise RuntimeError(
                f"No provider directory found for '{provider_name}' "
                f"and fallback '{DEFAULT_PROVIDER}' is missing."
            )

    if not provider_from_env and provider_detected == provider_name:
        print(f"[ricer-mcp] Auto-detected provider: '{provider_name}'")

    features_dir = os.path.join(provider_root, "features")
    features_init = os.path.join(features_dir, "__init__.py")
    utils_dir = os.path.join(provider_root, "utils")

    if not os.path.isdir(features_dir) or not os.path.isfile(features_init):
        raise RuntimeError(
            f"Provider '{provider_name}' is incomplete: expected features package "
            f"at '{features_init}'."
        )

    if not os.path.isdir(utils_dir):
        raise RuntimeError(
            f"Provider '{provider_name}' is incomplete: expected utils directory "
            f"at '{utils_dir}'."
        )

    for path in (root, provider_root):
        if path not in sys.path:
            sys.path.insert(0, path)

    return {
        "mcp_root": root,
        "provider_root": provider_root,
        "features_dir": features_dir,
        "utils_dir": utils_dir,
    }
