"""
Stack Visualization Panel
--------------------------
Displays the undo/redo stack with visual representation and control buttons.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QLabel,
    QFrame,
)


# ── Styles ───────────────────────────────────────────────────────────

PANEL_STYLE = """
    QWidget { background: #313244; }
"""

PANEL_HEADER_STYLE = """
    QLabel {
        color: #f5c2e7;
        font-size: 14px;
        font-weight: bold;
        padding: 6px 0px;
    }
"""

UNDO_REDO_BTN_STYLE = """
    QPushButton {
        background: #89b4fa;
        color: #1e1e2e;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: bold;
        min-width: 60px;
    }
    QPushButton:hover { background: #74c7ec; }
    QPushButton:disabled { background: #45475a; color: #6c7086; }
"""

STACK_ITEM_STYLE_ACTIVE = """
    QFrame {
        background: #45475a;
        border: 2px solid #89b4fa;
        border-radius: 6px;
        padding: 8px;
    }
"""

STACK_ITEM_STYLE_INACTIVE = """
    QFrame {
        background: #1e1e2e;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 8px;
    }
"""

STACK_ITEM_TEXT_ACTIVE = """
    color: #cdd6f4;
    font-size: 12px;
    font-weight: bold;
"""

STACK_ITEM_TEXT_INACTIVE = """
    color: #6c7086;
    font-size: 12px;
"""

SCROLL_AREA_STYLE = """
    QScrollArea { 
        border: 1px solid #45475a;
        background: #1e1e2e;
        border-radius: 6px;
    }
    QScrollBar:vertical {
        background: #1e1e2e;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #45475a;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover { background: #585b70; }
"""


# ── Stack Item Widget ────────────────────────────────────────────────

class StackItemWidget(QFrame):
    """A single item in the undo/redo stack."""

    def __init__(self, index: int, description: str, is_active: bool = False) -> None:
        super().__init__()
        self.index = index
        self.description = description
        self._is_active = is_active

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        # Index indicator
        index_label = QLabel(f"#{index}")
        index_label.setFont(QFont("Monospace", 10, QFont.Bold))
        layout.addWidget(index_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Default", 10))
        layout.addWidget(desc_label)

        self._set_active(is_active)

    def _set_active(self, active: bool) -> None:
        """Update styling based on active state."""
        self._is_active = active
        if active:
            self.setStyleSheet(STACK_ITEM_STYLE_ACTIVE)
        else:
            self.setStyleSheet(STACK_ITEM_STYLE_INACTIVE)

    def set_active(self, active: bool) -> None:
        """Public method to change active state."""
        self._set_active(active)

    def is_active(self) -> bool:
        return self._is_active


# ── Stack Panel Widget ───────────────────────────────────────────────

class StackPanel(QWidget):
    """Left sidebar showing the undo/redo stack with visual representation.
    
    This is a pure UI component. All stack logic is managed by StateManager
    in system-utils. The UI only:
    - Displays the stack items visually
    - Emits signals when undo/redo buttons are clicked
    - Updates display based on backend state changes
    """

    # Signals
    undo_requested = Signal()
    redo_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        
        # UI state only
        self._stack_items: list[StackItemWidget] = []
        self._current_index = -1  # For display purposes only

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the panel UI."""
        self.setStyleSheet(PANEL_STYLE)
        self.setMinimumWidth(220)
        self.setMaximumWidth(280)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ── Header ───────────────────────────────────────────────────
        header = QLabel("Stack")
        header.setStyleSheet(PANEL_HEADER_STYLE)
        main_layout.addWidget(header)

        # ── Control buttons ──────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._undo_btn = QPushButton("↶ Undo")
        self._undo_btn.setStyleSheet(UNDO_REDO_BTN_STYLE)
        self._undo_btn.clicked.connect(self.undo_requested.emit)
        self._undo_btn.setEnabled(False)
        btn_row.addWidget(self._undo_btn)

        self._redo_btn = QPushButton("↷ Redo")
        self._redo_btn.setStyleSheet(UNDO_REDO_BTN_STYLE)
        self._redo_btn.clicked.connect(self.redo_requested.emit)
        self._redo_btn.setEnabled(False)
        btn_row.addWidget(self._redo_btn)

        main_layout.addLayout(btn_row)

        # ── Scrollable stack view ────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(SCROLL_AREA_STYLE)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._stack_widget = QWidget()
        self._stack_layout = QVBoxLayout(self._stack_widget)
        self._stack_layout.setContentsMargins(0, 0, 0, 0)
        self._stack_layout.setSpacing(6)
        self._stack_layout.setAlignment(Qt.AlignTop)

        self._scroll.setWidget(self._stack_widget)
        main_layout.addWidget(self._scroll, stretch=1)

        # ── Info label ───────────────────────────────────────────────
        self._info_label = QLabel("Stack is empty")
        self._info_label.setStyleSheet(
            "color: #6c7086; font-size: 11px; padding: 6px 0px;"
        )
        self._info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self._info_label)

    # ── Public API (UI display only) ─────────────────────────────────

    def add_item_to_display(self, index: int, description: str, is_active: bool = False) -> None:
        """Add a visual item to the stack display.
        
        Called by ChatWindow when backend records a new change.
        All stack logic is in system-utils StateManager.
        """
        # Deactivate previous active item
        if self._stack_items:
            self._stack_items[-1].set_active(False)
        
        # Add new item
        item_widget = StackItemWidget(index, description, is_active=is_active)
        self._stack_items.append(item_widget)
        self._stack_layout.addWidget(item_widget)

        self._current_index = index
        self._update_info()

    def update_active_item(self, index: int) -> None:
        """Update which item is visually active (after undo/redo)."""
        # Deactivate all, activate the specified one
        for i, widget in enumerate(self._stack_items):
            widget.set_active(i == index)
        
        self._current_index = index
        self._update_info()

    def clear(self) -> None:
        """Clear all visual items from the display."""
        while self._stack_layout.count():
            item_widget = self._stack_layout.takeAt(0).widget()
            if item_widget:
                item_widget.deleteLater()

        self._stack_items = []
        self._current_index = -1
        self._update_info()

    def set_button_states(self, can_undo: bool, can_redo: bool) -> None:
        """Update button enabled states based on backend state."""
        self._undo_btn.setEnabled(can_undo)
        self._redo_btn.setEnabled(can_redo)

    # ── Internal helpers ─────────────────────────────────────────────

    def _update_info(self) -> None:
        """Update the info label."""
        if not self._stack_items:
            self._info_label.setText("Stack is empty")
        else:
            self._info_label.setText(
                f"Position: {self._current_index + 1} / {len(self._stack_items)}"
            )
