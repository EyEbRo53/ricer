"""Feature-oriented MCP registration (one module per setting)."""

from feature import Feature

from . import cursor_size
from . import double_click_interval
from . import single_click
from . import touchpad_settings
from . import keyboard_accessibility
from . import global_scaling
from . import window_borders
from . import wallpaper
from . import panel_position


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
