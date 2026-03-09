"""
Session Logger
--------------
Logs all chat I/O, tool calls, and changeset activity to a
timestamped log file under logs/.

Each session gets its own file: logs/session_YYYYMMDD_HHMMSS.log
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime


_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")


def get_logger(name: str = "ricer") -> logging.Logger:
    """Return (and lazily configure) the shared session logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    os.makedirs(_LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(_LOG_DIR, f"session_{timestamp}.log")

    fmt = logging.Formatter(
        "%(asctime)s  [%(levelname)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)

    logger.info("Session started — log file: %s", log_path)
    return logger


# ── Convenience helpers ──────────────────────────────────────────────

def log_user_message(text: str) -> None:
    get_logger().info("USER  ▸ %s", text)


def log_assistant_reply(text: str) -> None:
    get_logger().info("ASSISTANT  ▸ %s", text)


def log_tool_call(name: str, args: dict) -> None:
    get_logger().info("TOOL CALL  ▸ %s(%s)", name, json.dumps(args))


def log_tool_result(name: str, result: str) -> None:
    get_logger().info("TOOL RESULT  ▸ %s → %s", name, result)


def log_changeset_staged(receipt: dict) -> None:
    get_logger().info(
        "CHANGESET STAGED  ▸ #%s — %s  [script=%s, params=%s]",
        receipt.get("order", "?"),
        receipt.get("description", "?"),
        receipt.get("script", "?"),
        json.dumps(receipt.get("parameters", {})),
    )


def log_error(msg: str) -> None:
    get_logger().error("ERROR  ▸ %s", msg)
