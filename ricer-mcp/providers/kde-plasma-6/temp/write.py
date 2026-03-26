from __future__ import annotations
from typing import Any
from changeset import changeset 

def stage_kde_change(
    file: str, 
    group: str, 
    key: str, 
    value: Any, 
    description: str,
    change_type: str = "display"
) -> dict[str, Any]:
    """Stages a kwriteconfig6 command into the in-memory changeset."""
    # Build the command string for the eventual execution phase
    script_cmd = f'kwriteconfig6 --file {file} --group "{group}" --key {key} "{value}"'
    
    params = {
        "file": file,
        "group": group,
        "key": key,
        "value": value
    }

    # Add to the singleton changeset
    return changeset.add(
        description=description,
        change_type=change_type,
        script=script_cmd,
        parameters=params
    )