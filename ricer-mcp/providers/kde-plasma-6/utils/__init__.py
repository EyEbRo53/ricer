"""KDE configuration utilities.

Submodules:
    read   - Read KDE/Plasma configuration
    write  - Write KDE/Plasma configuration
    reload - Reload KDE/Plasma services
"""
from .read import (
    read_kde_config,
    read_kde_configs,
    read_kscreen_doctor,
    read_current_wallpaper,
    read_panel_position,
)
from .write import (
    write_kde_config,
    write_kde_configs,
    run_kscreen_doctor,
    run_plasma_script,
)
from .reload import (
    reconfigure_kwin,
    reload_plasma_shell,
    restart_kded,
)

__all__ = [
    # read
    "read_kde_config",
    "read_kde_configs",
    "read_kscreen_doctor",
    "read_current_wallpaper",
    "read_panel_position",
    # write
    "write_kde_config",
    "write_kde_configs",
    "run_kscreen_doctor",
    "run_plasma_script",
    # reload
    "reconfigure_kwin",
    "reload_plasma_shell",
    "restart_kded",
]