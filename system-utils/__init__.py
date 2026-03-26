# NullSystemProvider: a no-op SystemProvider for fallback use
from typing import Any
from .provider_interface import SystemProvider

class NullSystemProvider:
	def execute_script(self, script_name: str, parameters: dict[str, Any]) -> bool:
		return False

	def read_state(self, script_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
		return {}

	def post_apply_input_change(self, change: dict[str, Any]) -> None:
		pass
"""System utilities for the Ricer desktop customisation tool."""
