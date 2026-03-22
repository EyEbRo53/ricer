import os
import platform
import subprocess
import importlib

def get_os_info():
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "OS Release": platform.release(),
        "Architecture": platform.machine(),
    }
    
    if info["OS"] == "Linux":
        # Get Linux distribution name and version.
        try:
            distro = importlib.import_module("distro")
            info["Distribution"] = f"{distro.name()} {distro.version()}".strip()
        except Exception:
            # Fallback when optional distro package is not installed.
            if hasattr(platform, "freedesktop_os_release"):
                info["Distribution"] = platform.freedesktop_os_release().get(
                    "PRETTY_NAME", "Unknown Linux"
                )
            else:
                info["Distribution"] = "Unknown Linux"

    return info

def get_ui_environment():
    ui_info = {
        "Desktop Environment": "Unknown",
        "Session Type": "Unknown",
        "DE Version": "Unknown"
    }

    # 1. Detect Session Type (Wayland vs X11)
    session_type = os.environ.get("XDG_SESSION_TYPE")
    if not session_type:
        # Fallback check
        if os.environ.get("WAYLAND_DISPLAY"):
            session_type = "wayland"
        elif os.environ.get("DISPLAY"):
            session_type = "x11"
    
    ui_info["Session Type"] = session_type if session_type else "No Display Detected"

    # 2. Detect Desktop Environment (KDE, GNOME, etc.)
    xdg_current = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
    desktop_session = os.environ.get("DESKTOP_SESSION", "").upper()
    de_marker = f"{xdg_current}:{desktop_session}"

    def _read_cmd_version(cmd):
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
            return output.split(" ")[-1] if output else "Unknown"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Unknown"
    
    kde_full_session = os.environ.get("KDE_FULL_SESSION") == "true"
    has_explicit_de_marker = bool(xdg_current or desktop_session)

    if "KDE" in de_marker or (kde_full_session and not has_explicit_de_marker):
        ui_info["Desktop Environment"] = "KDE Plasma"
        ui_info["DE Version"] = _read_cmd_version(["plasmashell", "--version"])
            
    elif "GNOME" in de_marker:
        ui_info["Desktop Environment"] = "GNOME"
        ui_info["DE Version"] = _read_cmd_version(["gnome-shell", "--version"])

    elif "CINNAMON" in de_marker:
        ui_info["Desktop Environment"] = "Cinnamon"
        ui_info["DE Version"] = _read_cmd_version(["cinnamon", "--version"])

    elif "XFCE" in de_marker:
        ui_info["Desktop Environment"] = "XFCE"
        ui_info["DE Version"] = _read_cmd_version(["xfce4-session", "--version"])

    elif "MATE" in de_marker:
        ui_info["Desktop Environment"] = "MATE"
        ui_info["DE Version"] = _read_cmd_version(["mate-session", "--version"])

    elif "LXQT" in de_marker:
        ui_info["Desktop Environment"] = "LXQt"
        ui_info["DE Version"] = _read_cmd_version(["lxqt-session", "--version"])
    
    elif platform.system() == "Windows":
        ui_info["Desktop Environment"] = "Windows Explorer"
    elif platform.system() == "Darwin":
        ui_info["Desktop Environment"] = "macOS Aqua"

    return ui_info

def main():
    os_data = get_os_info()
    ui_data = get_ui_environment()
    
    print("--- System Information ---")
    for key, val in os_data.items():
        print(f"{key}: {val}")
        
    print("\n--- UI Environment ---")
    full_ui_string = (
        f"{ui_data['Desktop Environment']} "
        f"{ui_data['DE Version']} "
        f"({ui_data['Session Type'].capitalize()})"
    )
    print(f"Detected UI: {full_ui_string}")

if __name__ == "__main__":
    main()