#!/usr/bin/env python3
"""Set global UI scaling for improved visibility."""
from utilities.write.kscreen_doctor import run_kscreen_doctor


def set_global_scaling(scale_value):
    """Apply global scaling via orchestrator (kscreen-doctor)."""
    return run_kscreen_doctor(f"output.1.scale.{scale_value}")


