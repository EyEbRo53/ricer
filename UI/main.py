"""
Ricer UI — Entry Point
----------------------
Launches the PySide6 chat window and connects it to the
ricer-client backend via a background worker thread.

Usage:
    cd UI && python main.py
"""

from __future__ import annotations

import sys
import os

# Ensure ricer-client is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ricer-client"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from worker import create_worker_thread
from chat_window import ChatWindow


def main() -> None:
    app = QApplication(sys.argv)

    # Spin up the async backend on a dedicated thread
    thread, worker = create_worker_thread()

    window = ChatWindow(worker)
    window.show()

    thread.start()

    # Ensure clean shutdown
    def on_quit() -> None:
        worker.shutdown()
        thread.quit()
        thread.wait(3000)

    app.aboutToQuit.connect(on_quit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
