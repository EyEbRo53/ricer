"""Feature-oriented MCP registration (one module per setting)."""

from feature import Feature

from .input import cursor_size
from .input import double_click_interval
from .input import single_click
from .input import touchpad_settings
from .input import keyboard_accessibility
from .display import global_scaling
from .display import window_borders
from .display import wallpaper
from .display import panel_position
from .display import color_scheme

from .audio import system_sounds
from .audio import notifications
from .power import power_management
from .power import screen_locking
from .power import session_management
from .workspace import virtual_desktops
from .workspace import activities
from .workspace import task_switcher
from .workspace import workspace_behavior
from .workspace import screen_edges
from .workspace import blur_strength
from .workspace import launch_feedback
from .input import mouse_settings
from .input import global_shortcuts
from .input import bluetooth
from .apps import baloo_indexer
from .apps import dolphin_settings
from .apps import spectacle_settings
from .apps import konsole_misc
from .apps import autostart

_FEATURE_MODULES = (
    cursor_size,
    double_click_interval,
    single_click,
    touchpad_settings,
    keyboard_accessibility,
    global_scaling,
    window_borders,
    wallpaper,
    panel_position,
    color_scheme,
    system_sounds,
    notifications,
    power_management,
    screen_locking,
    session_management,
    virtual_desktops,
    activities,
    task_switcher,
    workspace_behavior,
    screen_edges,
    blur_strength,
    launch_feedback,
    mouse_settings,
    global_shortcuts,
    bluetooth,
    baloo_indexer,
    dolphin_settings,
    spectacle_settings,
    konsole_misc,
    autostart,
)


def _validate_feature_module(module) -> None:
    """Fail fast when a feature module does not expose the required contract."""
    module_name = module.__name__
    feature_obj = getattr(module, "feature", None)
    if feature_obj is None:
        raise RuntimeError(
            f"Feature module '{module_name}' must define a module-level 'feature' instance."
        )

    if not isinstance(feature_obj, Feature):
        raise RuntimeError(
            f"Feature module '{module_name}' has invalid 'feature': "
            f"expected Feature instance, got {type(feature_obj).__name__}."
        )

    if not callable(getattr(feature_obj, "set", None)):
        raise RuntimeError(
            f"Feature module '{module_name}' must implement feature.set(...)."
        )

    if not callable(getattr(feature_obj, "get", None)):
        raise RuntimeError(
            f"Feature module '{module_name}' must implement feature.get()."
        )

    register_fn = getattr(module, "register", None)
    if not callable(register_fn):
        raise RuntimeError(
            f"Feature module '{module_name}' must define callable register(mcp, changeset)."
        )


def register_all(mcp, changeset):
    """Register every feature module (tool + resource) on the MCP server."""
    for module in _FEATURE_MODULES:
        _validate_feature_module(module)
        module.register(mcp, changeset)
