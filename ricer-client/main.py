"""
Ricer Client — CLI Chat
-----------------------
Minimal terminal chat loop. Will be replaced with a GUI later,
but useful for testing the full pipeline right now.

Usage:
    python main.py
"""

from __future__ import annotations

import asyncio
import os
import sys

from mcp_client import MCPClient
from llm_provider import LLMConfig, create_llm_client
from orchestrator import Orchestrator


async def run() -> None:
    config = LLMConfig.from_env()
    llm = create_llm_client(config)
    mcp = MCPClient()

    print(f"[ricer] LLM provider : {config.provider} ({config.model})")
    print(f"[ricer] Connecting to MCP server …")

    await mcp.connect()

    orchestrator = Orchestrator(llm, config, mcp)

    # Show available resources to the LLM context on startup
    if mcp.resources:
        resource_list = "\n".join(
            f"  • {r['name']}  →  {r['uri']}" for r in mcp.resources
        )
        print(f"[ricer] Available resources:\n{resource_list}")

    print()
    print("╭───────────────────────────────────────────╮")
    print("│   Ricer — KDE Plasma Customisation Chat   │")
    print("│   Type 'quit' to exit, 'clear' to reset   │")
    print("╰───────────────────────────────────────────╯")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Bye!")
            break
        if user_input.lower() == "clear":
            orchestrator.clear_history()
            print("[ricer] Conversation cleared.\n")
            continue

        try:
            reply = await orchestrator.chat(user_input)
            print(f"\nRicer: {reply}\n")
        except Exception as exc:
            print(f"\n[error] {exc}\n")

    await mcp.disconnect()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
