"""
Chat Window
------------
Main application window — chat message area, input field, and send button.
"""

from __future__ import annotations

import json

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from worker import BackendWorker


# ── Styles ───────────────────────────────────────────────────────────

WINDOW_STYLE = """
    QMainWindow { background: #1e1e2e; }
"""

SCROLL_AREA_STYLE = """
    QScrollArea { border: none; background: #1e1e2e; }
"""

INPUT_STYLE = """
    QLineEdit {
        background: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 14px;
    }
    QLineEdit:focus { border-color: #89b4fa; }
"""

SEND_BTN_STYLE = """
    QPushButton {
        background: #89b4fa;
        color: #1e1e2e;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton:hover { background: #74c7ec; }
    QPushButton:disabled { background: #45475a; color: #6c7086; }
"""

USER_BUBBLE_STYLE = """
    background: #89b4fa; color: #1e1e2e;
    border-radius: 12px; padding: 10px 14px;
    font-size: 14px;
"""

ASSISTANT_BUBBLE_STYLE = """
    background: #313244; color: #cdd6f4;
    border-radius: 12px; padding: 10px 14px;
    font-size: 14px;
"""

STATUS_STYLE = """
    QLabel {
        color: #6c7086;
        font-size: 12px;
        padding: 4px 8px;
    }
"""

CHANGESET_CARD_STYLE = """
    background: #1e1e2e;
    border: 1px solid #f9e2af;
    border-radius: 10px;
    padding: 10px 14px;
"""

CHANGESET_TITLE_STYLE = """
    color: #f9e2af;
    font-size: 12px;
    font-weight: bold;
"""

CHANGESET_DESC_STYLE = """
    color: #cdd6f4;
    font-size: 13px;
"""

CHANGESET_META_STYLE = """
    color: #6c7086;
    font-size: 11px;
"""

TOOL_CALL_STYLE = """
    background: #181825;
    border-left: 3px solid #89b4fa;
    border-radius: 4px;
    padding: 6px 10px;
    color: #6c7086;
    font-size: 12px;
"""

CONFIRM_BTN_STYLE = """
    QPushButton {
        background: #a6e3a1; color: #1e1e2e;
        border: none; border-radius: 6px;
        padding: 4px 14px; font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #94e2d5; }
    QPushButton:disabled { background: #45475a; color: #6c7086; }
"""

SKIP_BTN_STYLE = """
    QPushButton {
        background: #f38ba8; color: #1e1e2e;
        border: none; border-radius: 6px;
        padding: 4px 14px; font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #eba0ac; }
    QPushButton:disabled { background: #45475a; color: #6c7086; }
"""

ACCEPT_ALL_BTN_STYLE = """
    QPushButton {
        background: #f9e2af; color: #1e1e2e;
        border: none; border-radius: 8px;
        padding: 6px 18px; font-size: 13px; font-weight: bold;
    }
    QPushButton:hover { background: #f5c2e7; }
    QPushButton:disabled { background: #45475a; color: #6c7086; }
"""

CHANGESET_APPLIED_STYLE = """
    background: #1e1e2e;
    border: 1px solid #a6e3a1;
    border-radius: 10px;
    padding: 10px 14px;
"""

CHANGESET_SKIPPED_STYLE = """
    background: #1e1e2e;
    border: 1px solid #6c7086;
    border-radius: 10px;
    padding: 10px 14px;
"""

CHANGESET_FAILED_STYLE = """
    background: #1e1e2e;
    border: 1px solid #f38ba8;
    border-radius: 10px;
    padding: 10px 14px;
"""


# ── Helper: message bubble ──────────────────────────────────────────

def _make_bubble(text: str, is_user: bool) -> QWidget:
    """Create a single chat bubble widget."""
    row = QHBoxLayout()
    row.setContentsMargins(8, 2, 8, 2)

    label = QLabel(text)
    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    label.setMaximumWidth(520)
    label.setStyleSheet(USER_BUBBLE_STYLE if is_user else ASSISTANT_BUBBLE_STYLE)

    if is_user:
        row.addStretch()
        row.addWidget(label)
    else:
        row.addWidget(label)
        row.addStretch()

    container = QWidget()
    container.setLayout(row)
    return container


def _make_changeset_card_static(receipt: dict) -> QWidget:
    """Create a changeset card showing order, description, and params.

    This is the non-interactive version kept for reference.
    The ChatWindow class builds interactive cards with buttons instead.
    """
    card_layout = QVBoxLayout()
    card_layout.setSpacing(4)
    card_layout.setContentsMargins(0, 0, 0, 0)

    order = receipt.get("order", "?")
    status = receipt.get("status", "staged")
    desc = receipt.get("description", "Unknown change")
    script = receipt.get("script", "")
    params = receipt.get("parameters", {})

    # Title line
    title = QLabel(f"📋  Change #{order}  —  {status}")
    title.setStyleSheet(CHANGESET_TITLE_STYLE)
    card_layout.addWidget(title)

    # Description
    desc_label = QLabel(desc)
    desc_label.setWordWrap(True)
    desc_label.setStyleSheet(CHANGESET_DESC_STYLE)
    card_layout.addWidget(desc_label)

    # Params summary
    if params:
        parts = [f"{k}={v}" for k, v in params.items()]
        meta = QLabel(f"script: {script}  •  {', '.join(parts)}")
        meta.setWordWrap(True)
        meta.setStyleSheet(CHANGESET_META_STYLE)
        card_layout.addWidget(meta)

    card = QWidget()
    card.setLayout(card_layout)
    card.setStyleSheet(CHANGESET_CARD_STYLE)
    card.setMaximumWidth(540)

    # Wrap in a row (left-aligned like assistant messages)
    row = QHBoxLayout()
    row.setContentsMargins(8, 4, 8, 4)
    row.addWidget(card)
    row.addStretch()

    container = QWidget()
    container.setLayout(row)
    return container


def _make_tool_indicator(name: str) -> QWidget:
    """Small inline indicator that a tool is being called."""
    row = QHBoxLayout()
    row.setContentsMargins(8, 1, 8, 1)

    label = QLabel(f"⚙  Calling {name}…")
    label.setStyleSheet(TOOL_CALL_STYLE)
    label.setMaximumWidth(400)

    row.addWidget(label)
    row.addStretch()

    container = QWidget()
    container.setLayout(row)
    return container


# ── Main Window ──────────────────────────────────────────────────────

class ChatWindow(QMainWindow):
    """Ricer desktop-customisation chat interface."""

    def __init__(self, worker: BackendWorker) -> None:
        super().__init__()
        self._worker = worker

        # Per-card tracking:  order → {card, title, confirm, skip}
        self._change_cards: dict[int, dict] = {}
        # Current batch of staged order numbers (reset each LLM turn)
        self._current_batch_orders: list[int] = []
        self._accept_all_shown = False
        self._accept_all_btn: QPushButton | None = None

        self._setup_ui()
        self._connect_signals()

    # ── UI construction ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setWindowTitle("Ricer — KDE Plasma Customisation")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        self.setStyleSheet(WINDOW_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Status bar at top ────────────────────────────────────────
        self._status_label = QLabel("Starting…")
        self._status_label.setStyleSheet(STATUS_STYLE)
        layout.addWidget(self._status_label)

        # ── Scrollable message area ──────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(SCROLL_AREA_STYLE)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._messages_widget = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setAlignment(Qt.AlignTop)
        self._messages_layout.setSpacing(4)
        self._messages_layout.setContentsMargins(4, 8, 4, 8)

        self._scroll.setWidget(self._messages_widget)
        layout.addWidget(self._scroll, stretch=1)

        # ── Input row at bottom ──────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setContentsMargins(8, 6, 8, 8)
        input_row.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask Ricer to customise your desktop…")
        self._input.setStyleSheet(INPUT_STYLE)

        self._send_btn = QPushButton("Send")
        self._send_btn.setStyleSheet(SEND_BTN_STYLE)

        input_row.addWidget(self._input, stretch=1)
        input_row.addWidget(self._send_btn)
        layout.addLayout(input_row)

    # ── Signal wiring ────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        # UI → Worker
        self._send_btn.clicked.connect(self._on_send)
        self._input.returnPressed.connect(self._on_send)

        # Worker → UI
        self._worker.reply_ready.connect(self._on_reply)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.status_changed.connect(self._on_status)
        self._worker.busy_changed.connect(self._on_busy)
        self._worker.tool_called.connect(self._on_tool_called)
        self._worker.changeset_staged.connect(self._on_changeset_staged)

        # Change-execution results
        self._worker.change_applied.connect(self._on_change_applied)
        self._worker.change_skipped.connect(self._on_change_skipped)
        self._worker.change_failed.connect(self._on_change_failed)

    # ── Slots ────────────────────────────────────────────────────────

    @Slot()
    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._add_message(text, is_user=True)
        self._input.clear()
        self._worker.send_message(text)

    @Slot(str)
    def _on_reply(self, text: str) -> None:
        self._add_message(text, is_user=False)

    @Slot(str)
    def _on_error(self, text: str) -> None:
        self._add_message(f"⚠ {text}", is_user=False)

    @Slot(str)
    def _on_status(self, text: str) -> None:
        self._status_label.setText(text)

    @Slot(bool)
    def _on_busy(self, busy: bool) -> None:
        self._send_btn.setEnabled(not busy)
        self._input.setEnabled(not busy)
        if busy:
            self._status_label.setText("Thinking…")
            # Reset batch tracking for the new LLM turn
            self._current_batch_orders = []
            self._accept_all_shown = False
            self._accept_all_btn = None
        else:
            self._status_label.setText("Ready")

    @Slot(str, str)
    def _on_tool_called(self, name: str, args_json: str) -> None:
        widget = _make_tool_indicator(name)
        self._messages_layout.addWidget(widget)
        QTimer.singleShot(50, self._scroll_to_bottom)

    @Slot(str)
    def _on_changeset_staged(self, receipt_json: str) -> None:
        try:
            receipt = json.loads(receipt_json)
        except json.JSONDecodeError:
            return

        order = receipt.get("order", 0)

        # Insert an "Accept All" button before the first card in the batch
        if not self._accept_all_shown:
            self._add_accept_all_button()
            self._accept_all_shown = True

        self._current_batch_orders.append(order)

        # Build the interactive card and add it
        card_widget = self._make_changeset_card(receipt)
        self._messages_layout.addWidget(card_widget)
        QTimer.singleShot(50, self._scroll_to_bottom)

    # ── Change-result slots ──────────────────────────────────────────

    @Slot(int)
    def _on_change_applied(self, order: int) -> None:
        refs = self._change_cards.get(order)
        if not refs:
            return
        refs["title"].setText(f"✅  Change #{order}  —  applied")
        refs["card"].setStyleSheet(CHANGESET_APPLIED_STYLE)
        refs["confirm"].setEnabled(False)
        refs["skip"].setEnabled(False)

    @Slot(int)
    def _on_change_skipped(self, order: int) -> None:
        refs = self._change_cards.get(order)
        if not refs:
            return
        refs["title"].setText(f"⏭  Change #{order}  —  skipped")
        refs["card"].setStyleSheet(CHANGESET_SKIPPED_STYLE)
        refs["confirm"].setEnabled(False)
        refs["skip"].setEnabled(False)

    @Slot(int, str)
    def _on_change_failed(self, order: int, error: str) -> None:
        refs = self._change_cards.get(order)
        if not refs:
            return
        refs["title"].setText(f"❌  Change #{order}  —  failed ({error})")
        refs["card"].setStyleSheet(CHANGESET_FAILED_STYLE)
        refs["confirm"].setEnabled(False)
        refs["skip"].setEnabled(False)

    # ── Interactive card builder ─────────────────────────────────────

    def _make_changeset_card(self, receipt: dict) -> QWidget:
        """Build a changeset card with Confirm / Skip buttons."""
        order = receipt.get("order", "?")
        status = receipt.get("status", "staged")
        desc = receipt.get("description", "Unknown change")
        script = receipt.get("script", "")
        params = receipt.get("parameters", {})

        card_layout = QVBoxLayout()
        card_layout.setSpacing(4)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel(f"📋  Change #{order}  —  {status}")
        title.setStyleSheet(CHANGESET_TITLE_STYLE)
        card_layout.addWidget(title)

        # Description
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(CHANGESET_DESC_STYLE)
        card_layout.addWidget(desc_label)

        # Params summary
        if params:
            parts = [f"{k}={v}" for k, v in params.items()]
            meta = QLabel(f"script: {script}  •  {', '.join(parts)}")
            meta.setWordWrap(True)
            meta.setStyleSheet(CHANGESET_META_STYLE)
            card_layout.addWidget(meta)

        # ── Confirm / Skip buttons ───────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 0)
        btn_row.setSpacing(6)

        confirm_btn = QPushButton("✓ Confirm")
        confirm_btn.setStyleSheet(CONFIRM_BTN_STYLE)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(lambda _, o=order: self._on_confirm_clicked(o))

        skip_btn = QPushButton("✗ Skip")
        skip_btn.setStyleSheet(SKIP_BTN_STYLE)
        skip_btn.setCursor(Qt.PointingHandCursor)
        skip_btn.clicked.connect(lambda _, o=order: self._on_skip_clicked(o))

        btn_row.addWidget(confirm_btn)
        btn_row.addWidget(skip_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        # Assemble card widget
        card = QWidget()
        card.setLayout(card_layout)
        card.setStyleSheet(CHANGESET_CARD_STYLE)
        card.setMaximumWidth(540)

        # Store references for later updates
        self._change_cards[order] = {
            "card": card,
            "title": title,
            "confirm": confirm_btn,
            "skip": skip_btn,
        }

        # Wrap in a left-aligned row
        row = QHBoxLayout()
        row.setContentsMargins(8, 4, 8, 4)
        row.addWidget(card)
        row.addStretch()

        container = QWidget()
        container.setLayout(row)
        return container

    def _add_accept_all_button(self) -> None:
        """Insert an 'Accept All' button above the first card in the batch."""
        btn = QPushButton("✓  Accept All Changes")
        btn.setStyleSheet(ACCEPT_ALL_BTN_STYLE)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._on_accept_all_clicked)
        self._accept_all_btn = btn

        row = QHBoxLayout()
        row.setContentsMargins(8, 6, 8, 2)
        row.addWidget(btn)
        row.addStretch()

        container = QWidget()
        container.setLayout(row)
        self._messages_layout.addWidget(container)

    # ── Button handlers ──────────────────────────────────────────────

    def _on_confirm_clicked(self, order: int) -> None:
        refs = self._change_cards.get(order)
        if refs:
            refs["confirm"].setEnabled(False)
            refs["skip"].setEnabled(False)
            refs["title"].setText(f"⏳  Change #{order}  —  applying…")
        self._worker.confirm_change(order)

    def _on_skip_clicked(self, order: int) -> None:
        self._worker.skip_change(order)

    def _on_accept_all_clicked(self) -> None:
        if self._accept_all_btn:
            self._accept_all_btn.setEnabled(False)
            self._accept_all_btn.setText("Applying all…")
        # Disable every card's buttons
        for order in self._current_batch_orders:
            refs = self._change_cards.get(order)
            if refs:
                refs["confirm"].setEnabled(False)
                refs["skip"].setEnabled(False)
                refs["title"].setText(
                    f"⏳  Change #{order}  —  applying…"
                )
        self._worker.confirm_batch(list(self._current_batch_orders))

    # ── Helpers ──────────────────────────────────────────────────────

    def _add_message(self, text: str, *, is_user: bool) -> None:
        bubble = _make_bubble(text, is_user)
        self._messages_layout.addWidget(bubble)
        # Delay scroll so layout has time to update
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())
