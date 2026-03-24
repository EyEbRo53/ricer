"""Feature-oriented MCP registration (one module per setting)."""

from feature import Feature

from .display import wallpaper
from .display import gtk_theme
from .display import icon_theme
from .input import cursor_size
from .workspace import workspaces

_FEATURE_MODULES = (
    wallpaper,
    gtk_theme,
    icon_theme,
    cursor_size,
    workspaces,
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
