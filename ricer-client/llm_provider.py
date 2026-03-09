"""
LLM Provider Configuration
---------------------------
Loads env vars and exposes a configured OpenAI-compatible client.

Every supported provider (OpenAI, Gemini, Grok, Ollama) exposes an
OpenAI-compatible chat completions endpoint, so we only need one
client class — just swap base_url and api_key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# ── Provider presets ─────────────────────────────────────────────────

_PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
    },
    "grok": {
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "GROK_API_KEY",
        "default_model": "grok-3",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
    },
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "api_key_env": "",
        "default_model": "llama3.1",
    },
}


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    base_url: str
    api_key: str

    @classmethod
    def from_env(cls) -> LLMConfig:
        """Build config from environment variables."""
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if provider not in _PROVIDER_DEFAULTS:
            raise ValueError(
                f"Unknown LLM_PROVIDER '{provider}'. "
                f"Choose from: {', '.join(_PROVIDER_DEFAULTS)}"
            )

        preset = _PROVIDER_DEFAULTS[provider]
        api_key = (
            os.getenv(preset["api_key_env"], "") if preset["api_key_env"] else "ollama"
        )
        model = os.getenv("LLM_MODEL") or preset["default_model"]

        return cls(
            provider=provider,
            model=model,
            base_url=preset["base_url"],
            api_key=api_key,
        )


def create_llm_client(config: LLMConfig | None = None) -> AsyncOpenAI:
    """Return an async OpenAI-compatible client for the active provider."""
    if config is None:
        config = LLMConfig.from_env()

    return AsyncOpenAI(
        api_key=config.api_key,
        base_url=config.base_url,
    )
