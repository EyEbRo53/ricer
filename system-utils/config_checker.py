"""Config Checker.

Pure verification utility with no script-specific knowledge.
"""

from __future__ import annotations


class ConfigChecker:
    """Compares snapshots against expected parameters."""

    @staticmethod
    def _is_close(a: object, b: object, tol: float = 0.01) -> bool:
        try:
            return abs(float(a) - float(b)) < tol
        except (TypeError, ValueError):
            return False

    def verify(self, before: dict, after: dict, parameters: dict) -> bool:
        """Validate the post-change snapshot against requested parameters.

        Rules:
        - Every expected parameter key must exist in ``after``.
        - Float values are compared with a small tolerance.
        - Other values are compared as normalized strings.
        """
        for key, expected in parameters.items():
            if key not in after:
                return False

            current = after.get(key)
            if isinstance(expected, float):
                if not self._is_close(current, expected):
                    return False
                continue

            if str(current).strip().lower() != str(expected).strip().lower():
                return False

        # ``before`` is intentionally accepted for symmetric API use by
        # OrderManager even though verification is parameter-driven.
        _ = before
        return True

    def reverse_parameters(self, config_snapshot: dict) -> dict:
        """Build reversal parameters directly from a snapshot dict."""
        return {
            key: value
            for key, value in config_snapshot.items()
            if value is not None
        }
