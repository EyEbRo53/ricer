"""Write utilities for KDE Plasma configuration."""
from .kwriteconfig import write_kde_config, write_kde_configs
from .kscreen_doctor import run_kscreen_doctor
from .plasma_script import run_plasma_script

__all__ = [
    "write_kde_config",
    "write_kde_configs",
    "run_kscreen_doctor",
    "run_plasma_script",
]
