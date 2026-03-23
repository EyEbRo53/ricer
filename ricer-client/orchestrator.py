"""
Orchestrator
------------
The core loop that ties the LLM and MCP server together.

1. User sends a message.
2. We send the message (+ conversation history) to the LLM along
   with the MCP tool definitions.
3. If the LLM returns tool calls, we execute them on the MCP server
   and feed the results back to the LLM.
4. Repeat until the LLM produces a final text response.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from mcp_client import MCPClient
from llm_provider import LLMConfig

SYSTEM_PROMPT = """\
You are **Ricer**, a friendly KDE Plasma desktop customisation assistant.

You can READ the user's current desktop settings via resources and
STAGE changes via tools. Changes are NOT applied immediately — they
go into a changeset that the user must confirm.

Guidelines:
- Before making changes, read the relevant resource to show the user
  their current value.
- Never invent or assume current setting values. If a read fails,
    clearly state the failure and ask the user to retry.
- Explain what each change will do in plain language.
- After staging changes, remind the user to confirm or review the
  changeset.
- If the user's request is ambiguous, ask a clarifying question
  before staging anything.
- If a user reply is a confirmation like "yes", "sure", "go with it",
    it refers only to the single most recent option you proposed.
- Never stage multiple alternatives for the same setting in one turn.
- Be concise and helpful.
"""


def _build_system_prompt(resources: list[dict]) -> str:
    """Build system prompt with currently available resource URIs."""
    if not resources:
        return SYSTEM_PROMPT

    resource_lines = "\n".join(
        f"- {r['uri']}: {r.get('description') or r.get('name', '')}"
        for r in resources
    )

    return (
        f"{SYSTEM_PROMPT}\n"
        "Available resource URIs (read-only):\n"
        f"{resource_lines}\n\n"
        "When the user asks to view/read/check a current setting, call the "
        "`read_resource` tool with the best matching URI before replying."
    )


class Orchestrator:
    """Coordinates LLM <-> MCP tool-call loop."""

    def __init__(
        self,
        llm_client: AsyncOpenAI,
        llm_config: LLMConfig,
        mcp: MCPClient,
        on_tool_call: Callable[[str, dict], None] | None = None,
        on_tool_result: Callable[[str, str], None] | None = None,
    ) -> None:
        self._llm = llm_client
        self._config = llm_config
        self._mcp = mcp
        self._on_tool_call = on_tool_call
        self._on_tool_result = on_tool_result
        self._history: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": _build_system_prompt(self._mcp.resources)}
        ]

    @staticmethod
    def _is_read_only_tool(fn_name: str) -> bool:
        """Return True when a tool call is known to be side-effect free."""
        return fn_name == "read_resource" or fn_name.startswith("get_")

    # ── Public API ───────────────────────────────────────────────────

    async def chat(self, user_message: str) -> str:
        """
        Send a user message and return the assistant's final text reply.
        Handles multi-turn tool-call loops transparently.
        """
        self._history.append({"role": "user", "content": user_message})

        max_retries = 3
        retries = 0

        while True:
            try:
                response = await self._llm.chat.completions.create(
                    model=self._config.model,
                    messages=self._history,
                    tools=self._mcp.get_openai_tools() or None,
                )
            except Exception as exc:
                error_msg = str(exc)
                # If the LLM hallucinated a tool name or produced a
                # malformed tool call, feed the error back so it can
                # self-correct on the next iteration.
                if retries < max_retries and (
                    "tool_use_failed" in error_msg
                    or "not in request.tools" in error_msg
                    or "tool call validation failed" in error_msg
                ):
                    retries += 1
                    self._history.append(
                        {
                            "role": "user",
                            "content": (
                                f"[SYSTEM: Your previous tool call failed "
                                f"with this error: {error_msg}. "
                                f"Please use only the tools provided. "
                                f"Review the available tools and try again.]"
                            ),
                        }
                    )
                    continue
                raise

            message = response.choices[0].message

            # ── No tool calls → final answer ─────────────────────────
            if not message.tool_calls:
                assistant_text = message.content or ""
                self._history.append(
                    {"role": "assistant", "content": assistant_text}
                )
                return assistant_text

            # ── Tool calls → execute each, feed results back ─────────
            # Append the assistant message that contains the tool calls
            self._history.append(message)  # type: ignore[arg-type]

            seen_mutating_tools: set[str] = set()

            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                print(f"  ⚙  Calling tool: {fn_name}({json.dumps(fn_args)})")
                if self._on_tool_call:
                    self._on_tool_call(fn_name, fn_args)

                try:
                    is_read_only = self._is_read_only_tool(fn_name)
                    if not is_read_only and fn_name in seen_mutating_tools:
                        raise RuntimeError(
                            "Duplicate mutating tool call blocked in a single turn: "
                            f"{fn_name}. Ask for clarification instead of staging "
                            "multiple alternatives."
                        )

                    if fn_name == "read_resource":
                        uri = fn_args.get("uri", "")
                        result = await self._mcp.read_resource(uri)
                    else:
                        result = await self._mcp.call_tool(fn_name, fn_args)

                    if not is_read_only:
                        seen_mutating_tools.add(fn_name)
                except Exception as exc:
                    result = f"Error: {exc}"

                if self._on_tool_result:
                    self._on_tool_result(fn_name, result)

                self._history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            # Loop back so the LLM can see the tool results

    # ── Helpers ──────────────────────────────────────────────────────

    def clear_history(self) -> None:
        """Reset conversation but keep the system prompt."""
        self._history = [
            {"role": "system", "content": _build_system_prompt(self._mcp.resources)}
        ]

    @property
    def history(self) -> list[ChatCompletionMessageParam]:
        return list(self._history)
