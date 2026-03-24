"""Cinnamon configuration writers via gsettings."""

from .gsettings_writer import write_gsetting, write_gsettings

__all__ = [
    "write_gsetting",
    "write_gsettings",
]
