"""
Async Backend Worker
--------------------
Bridges PySide6's Qt event loop with the asyncio-based orchestrator.

Runs its own asyncio event loop in a QThread so the UI never blocks.
Communicates via Qt signals.
"""

from __future__ import annotations

import asyncio
import json
import sys
import os

from PySide6.QtCore import QThread, Signal, QObject

# Allow imports from ricer-client and load its .env
_CLIENT_DIR = os.path.join(os.path.dirname(__file__), "..", "ricer-client")
_MCP_SERVER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ricer-mcp", "server.py")
)
sys.path.insert(0, _CLIENT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(_CLIENT_DIR, ".env"))

from mcp_client import MCPClient
from llm_provider import LLMConfig, create_llm_client
from orchestrator import Orchestrator
from logger import (
    log_user_message, log_assistant_reply, log_tool_call,
    log_tool_result, log_changeset_staged, log_error,
)


class BackendWorker(QObject):
    """Runs the Orchestrator in a background thread with its own event loop."""

    # Signals emitted back to the UI thread
    reply_ready = Signal(str)       # assistant reply text
    error_occurred = Signal(str)    # error message
    status_changed = Signal(str)    # connection status updates
    busy_changed = Signal(bool)     # True while waiting for LLM
    tool_called = Signal(str, str)  # (tool_name, args_json)
    changeset_staged = Signal(str)  # changeset receipt JSON

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._orchestrator: Orchestrator | None = None
        self._mcp: MCPClient | None = None

    # ── Thread entry point ───────────────────────────────────────────

    def run(self) -> None:
        """Called when the host QThread starts. Sets up asyncio + connects."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        # Connect first, then keep the loop alive for future coroutines
        self._loop.run_until_complete(self._connect())
        self._loop.run_forever()

    async def _connect(self) -> None:
        """Initialise LLM client, MCP connection, and orchestrator."""
        try:
            self.status_changed.emit("Connecting to MCP server…")

            config = LLMConfig.from_env()
            llm = create_llm_client(config)
            self._mcp = MCPClient(server_script=_MCP_SERVER)
            await self._mcp.connect()

            self._orchestrator = Orchestrator(
                llm, config, self._mcp,
                on_tool_call=self._handle_tool_call,
                on_tool_result=self._handle_tool_result,
            )

            self.status_changed.emit(
                f"Connected — {config.provider}/{config.model}"
            )
        except Exception as exc:
            self.error_occurred.emit(f"Connection failed: {exc}")

    # ── Public slot (called from UI thread) ──────────────────────────

    def send_message(self, text: str) -> None:
        """Schedule a chat message on the background event loop."""
        if self._loop is None or self._orchestrator is None:
            self.error_occurred.emit("Backend not connected yet.")
            return
        log_user_message(text)
        asyncio.run_coroutine_threadsafe(self._handle_chat(text), self._loop)

    def clear_history(self) -> None:
        """Reset conversation history."""
        if self._orchestrator:
            self._orchestrator.clear_history()

    async def _handle_chat(self, text: str) -> None:
        self.busy_changed.emit(True)
        try:
            reply = await self._orchestrator.chat(text)
            log_assistant_reply(reply)
            self.reply_ready.emit(reply)
        except Exception as exc:
            friendly = _friendly_error(exc)
            log_error(friendly)
            self.error_occurred.emit(friendly)
        finally:
            self.busy_changed.emit(False)

    # ── Tool-call callbacks (called from orchestrator) ───────────────

    def _handle_tool_call(self, name: str, args: dict) -> None:
        log_tool_call(name, args)
        self.tool_called.emit(name, json.dumps(args))

    def _handle_tool_result(self, name: str, result: str) -> None:
        log_tool_result(name, result)
        # Try to parse as changeset receipt
        try:
            receipt = json.loads(result)
            if isinstance(receipt, dict) and "order" in receipt and "description" in receipt:
                log_changeset_staged(receipt)
                self.changeset_staged.emit(result)
        except (json.JSONDecodeError, TypeError):
            pass

    # ── Cleanup ──────────────────────────────────────────────────────

    def shutdown(self) -> None:
        """Gracefully tear down the MCP connection and event loop."""
        if self._loop and self._mcp:
            future = asyncio.run_coroutine_threadsafe(
                self._mcp.disconnect(), self._loop
            )
            future.result(timeout=5)
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)


def _friendly_error(exc: Exception) -> str:
    """Turn verbose API errors into short, readable messages."""
    msg = str(exc)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        return "API quota exceeded. Check your plan or switch to a different provider (e.g. Ollama for local models)."
    if "401" in msg or "UNAUTHENTICATED" in msg:
        return "Invalid API key. Check GEMINI_API_KEY in ricer-client/.env."
    if "connection" in msg.lower() or "connect" in msg.lower():
        return f"Connection error: {msg.split(chr(10))[0]}"
    # Truncate overly long errors
    return msg[:300] if len(msg) > 300 else msg


def create_worker_thread() -> tuple[QThread, BackendWorker]:
    """Convenience factory: creates a QThread + BackendWorker pair."""
    thread = QThread()
    worker = BackendWorker()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    return thread, worker
