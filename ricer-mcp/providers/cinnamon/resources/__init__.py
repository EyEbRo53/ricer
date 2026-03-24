"""Provider-level read-only resources registration."""

from . import system_catalog


_RESOURCE_MODULES = (
    system_catalog,
)


def register_all(mcp) -> None:
    """Register all provider-level read-only resources."""
    for module in _RESOURCE_MODULES:
        register_fn = getattr(module, "register", None)
        if not callable(register_fn):
            raise RuntimeError(
                f"Resource module '{module.__name__}' must define callable register(mcp)."
            )
        register_fn(mcp)
