"""Base abstraction for all configurable KDE features."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Feature(ABC):
    """Common contract for MCP feature modules."""

    @abstractmethod
    def set(self, *args, **kwargs) -> bool:
        """Apply a confirmed change in the local desktop environment."""

    @abstractmethod
    def get(self) -> dict:
        """Read the current feature state from the local desktop environment."""

    def execute(self, *args, **kwargs) -> bool:
        """Backward-compatible alias for legacy call sites."""
        return self.set(*args, **kwargs)

    @abstractmethod
    def register_tool(self, mcp, changeset) -> None:
        """Register MCP tool(s) that stage this feature's changes."""

    @abstractmethod
    def register_resource(self, mcp) -> None:
        """Register MCP resource(s) that read this feature's current state."""

    def register(self, mcp, changeset) -> None:
        """Register both tool and resource for this feature."""
        self.register_tool(mcp, changeset)
        self.register_resource(mcp)
