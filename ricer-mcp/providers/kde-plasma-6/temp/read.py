import subprocess
from typing import Optional

def get_config_value(file: str, group: str, key: str, default: Optional[str] = None) -> str:
    """Executes kreadconfig6 to retrieve the current value of a KDE setting."""
    cmd = ["kreadconfig6", "--file", file, "--group", group, "--key", key]
    if default:
        cmd += ["--default", str(default)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""