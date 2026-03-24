"""Provider Interface
------------------
Defines the contract that any Desktop Environment (DE) provider must implement
for the system utilities to operate.
"""

from typing import Protocol, Any


class SystemProvider(Protocol):
    """Protocol defining the operations a DE provider must support."""

    def execute_script(self, script_name: str, parameters: dict[str, Any]) -> bool:
        """Run a configuration script by name with the given parameters.

        Args:
            script_name: The name of the script/feature to run.
            parameters: The parameters to apply.

        Returns:
            True if execution succeeded, False otherwise.
        """
        ...

    def read_state(self, script_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Read the current state for a given script configuration.

        Args:
            script_name: The name of the script/feature to read state for.
            parameters: The intended parameters, to help locate the correct state points.

        Returns:
            A dictionary representing the current configuration state.
        """
        ...

    def post_apply_input_change(self, change: dict[str, Any]) -> None:
        """Perform actions necessary after an input configuration changes (e.g. reload shell)."""
        ...
