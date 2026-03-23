#!/usr/bin/env python3
"""
Utility script to check for and install kde-cli-tools if needed.
Handles kquitapp6 and kstart dependency management.
Single responsibility: kde-cli-tools dependency checking and installation.
"""
import subprocess
import shutil


def is_kde_cli_tools_available():
    """
    Check if kde-cli-tools is available on the system.
    Returns True if at least one supported startup command is available.
    """
    return (
        shutil.which("kstart6") is not None
        or shutil.which("kstart") is not None
        or shutil.which("plasmashell") is not None
    )


def install_kde_cli_tools():
    """
    Install kde-cli-tools using pacman.
    Requires sudo privileges.
    Returns True on success, False on failure.
    """
    print("📦 Installing kde-cli-tools...")
    try:
        subprocess.run(
            ["sudo", "pacman", "-S", "--noconfirm", "kde-cli-tools"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✓ kde-cli-tools installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to install kde-cli-tools: {e.stderr}")
        return False
    except FileNotFoundError:
        print("⚠️  sudo or pacman not found. Cannot install kde-cli-tools.")
        return False


def ensure_kde_cli_tools():
    """
    Ensure kde-cli-tools is available, installing if necessary.
    Returns True if kde-cli-tools is available (either already was or was installed).
    Returns False if kde-cli-tools is not available and installation failed.
    """
    if is_kde_cli_tools_available():
        print("✓ kde-cli-tools already available")
        return True

    print("⚠️  kde-cli-tools not found. Attempting installation...")
    return install_kde_cli_tools()


if __name__ == "__main__":
    if ensure_kde_cli_tools():
        print("✅ kde-cli-tools is ready")
    else:
        print("❌ kde-cli-tools unavailable and could not be installed")
        exit(1)
