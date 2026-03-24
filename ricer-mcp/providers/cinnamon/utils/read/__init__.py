"""Cinnamon configuration readers via gsettings."""

from .gsettings_reader import read_gsetting, read_gsettings

__all__ = [
    "read_gsetting",
    "read_gsettings",
]
