#!/usr/bin/env python3
"""Configure touchpad sensitivity and acceleration."""
from utilities.kde_config_orchestrator import write_kde_configs


def set_touchpad_settings(acceleration, speed, deceleration):
    """Adjust touchpad sensitivity, acceleration and deceleration.

    Args:
        acceleration: Acceleration multiplier (e.g., 0.5, 1.0, 1.5)
        speed: Pointer speed (e.g., 1, 3, 5)
        deceleration: Deceleration multiplier (e.g., 1.0, 1.5)
    """
    configs = [
        ("kcminputrc", "Touchpad", "Acceleration", str(acceleration)),
        ("kcminputrc", "Touchpad", "Speed", str(speed)),
        ("kcminputrc", "Touchpad", "Deceleration", str(deceleration)),
    ]
    return write_kde_configs(configs)


if __name__ == "__main__":
    set_touchpad_settings(0.5, 3, 1.5)
