#!/usr/bin/env python3
"""
Live cursor size changer for Plasma 6 Wayland.

Does not restart KWin. Works immediately for all applications in the current session.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtCore import Qt


def set_cursor_size(size: int):
    """
    Sets the cursor size live.
    :param size: integer, desired cursor size in pixels
    """
    app = QApplication.instance() or QApplication(sys.argv)

    # Get current cursor pixmap and scale it
    current_cursor = QCursor()
    pixmap = current_cursor.pixmap()

    if pixmap.isNull():
        # fallback: use standard arrow cursor
        pixmap = QPixmap(":/cursors/arrow")

    scaled = pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    new_cursor = QCursor(scaled)
    QApplication.setOverrideCursor(new_cursor)
    print(f"Cursor size set to {size}px")


