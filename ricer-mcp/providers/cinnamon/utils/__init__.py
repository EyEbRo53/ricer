"""Cinnamon configuration utilities.

Submodules:
    read   - Read Cinnamon/GTK configuration via gsettings
    write  - Write Cinnamon/GTK configuration via gsettings
    reload - Reload Cinnamon desktop components
"""
from .read import (
    read_gsetting,
    read_gsettings,
)
from .write import (
    write_gsetting,
    write_gsettings,
)
from .reload import (
    reload_cinnamon,
    restart_cinnamon_settings,
)

__all__ = [
    # read
    "read_gsetting",
    "read_gsettings",
    # write
    "write_gsetting",
    "write_gsettings",
    # reload
    "reload_cinnamon",
    "restart_cinnamon_settings",
]
