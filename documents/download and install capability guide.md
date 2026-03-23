Methods to give mcp server download/install capability
To give an MCP server download and install capabilities, you need to configure it with appropriate permissions and access. Here's how:

---

## 🔧 Method 1: **MCP Server Configuration File**

Most MCP servers use a configuration file to define allowed operations. Create or modify `~/.config/mcp/config.json`:

```json
{
  "server": {
    "name": "kde-ricer",
    "allowed_commands": [
      "kwriteconfig6",
      "qdbus6",
      "kapplymousetheme",
      "kquitapp6",
      "kstart6",
      "kbuildsycoca6",
      "kcmshell6",
      "plasma-apply-*",
      "plasma-apply-wallpaperimage",
      "plasmapkg2"
    ],
    "allowed_network": [
      "raw.githubusercontent.com",
      "github.com",
      "store.kde.org",
      "*.tar.gz",
      "*.zip"
    ],
    "allowed_paths": [
      "~/.config/",
      "~/.local/share/",
      "/usr/share/icons/",
      "/usr/share/themes/"
    ],
    "install_commands": [
      "pacman -S --noconfirm",
      "yay -S --noconfirm",
      "flatpak install -y",
      "pip install"
    ],
    "download_tools": [
      "wget",
      "curl",
      "git clone"
    ]
  }
}
```

---

## 🔧 Method 2: **Environment Variables**

Set environment variables to give the MCP server extended permissions:

```bash
# Add to ~/.bashrc or ~/.zshrc
export MCP_ALLOW_COMMANDS="kwriteconfig6,qdbus6,plasmapkg2,wget,curl,git,pacman,flatpak"
export MCP_ALLOW_NETWORK="true"
export MCP_ALLOW_FILE_WRITE="~/.config/*,~/.local/share/*"
export MCP_ALLOW_INSTALL="true"
```

---

## 🔧 Method 3: **Custom MCP Server with Package Manager Access**

If you're building the MCP server yourself, add these capabilities:

```python
# Example Python-based MCP server with install capabilities
import subprocess
import os
import json

class KDERicingServer:
    def __init__(self):
        self.allowed_commands = [
            'kwriteconfig6', 'qdbus6', 'kapplymousetheme',
            'pacman', 'yay', 'flatpak', 'wget', 'curl', 'git'
        ]
    
    def execute_command(self, command, args):
        """Execute system commands with validation"""
        if command not in self.allowed_commands:
            return {"error": f"Command {command} not allowed"}
        
        try:
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}
    
    def install_theme(self, theme_name, source="aur"):
        """Install themes from various sources"""
        if source == "aur":
            return self.execute_command("yay", ["-S", "--noconfirm", theme_name])
        elif source == "flatpak":
            return self.execute_command("flatpak", ["install", "-y", theme_name])
        elif source == "url":
            # Download and install manually
            return self.install_from_url(theme_name)
    
    def install_from_url(self, url):
        """Download and install theme from URL"""
        # Download
        download = self.execute_command("wget", [url])
        if download["returncode"] != 0:
            return download
        
        # Extract if it's a tarball
        filename = url.split('/')[-1]
        if filename.endswith('.tar.gz'):
            extract = self.execute_command("tar", ["-xzf", filename])
            if extract["returncode"] != 0:
                return extract
            
            # Install with plasmapkg2
            folder = filename.replace('.tar.gz', '')
            install = self.execute_command("plasmapkg2", ["--type", "globaltheme", "--install", folder])
            return install
```

---

## 🔧 Method 4: **Sudo Access for Package Installation**

If the MCP server needs to install system packages, configure sudoers:

```bash
# Add to /etc/sudoers.d/mcp-server
# Allow MCP server to run package managers without password
mcp_user ALL=(ALL) NOPASSWD: /usr/bin/pacman, /usr/bin/yay, /usr/bin/flatpak

# Or allow specific commands only
mcp_user ALL=(ALL) NOPASSWD: /usr/bin/pacman -S *, /usr/bin/yay -S *
```

Then in the MCP server, use sudo for privileged operations:

```python
def install_system_package(self, package):
    """Install system package with sudo"""
    result = subprocess.run(
        ["sudo", "pacman", "-S", "--noconfirm", package],
        capture_output=True,
        text=True
    )
    return result.returncode == 0
```

---

## 🔧 Method 5: **User-Scoped Installation (No Sudo)**

For user-level installations that don't require root:

```bash
# Create user directories if they don't exist
mkdir -p ~/.local/share/plasma/desktoptheme/
mkdir -p ~/.local/share/icons/
mkdir -p ~/.local/share/color-schemes/

# Download and install theme locally
cd /tmp
wget https://github.com/user/win11-theme.tar.gz
tar -xzf win11-theme.tar.gz
cp -r win11-theme ~/.local/share/plasma/desktoptheme/

# Apply theme
kwriteconfig6 --file ~/.config/kdeglobals --group General --key ColorScheme "Win11"
```

---

## 🔧 Method 6: **Flatpak-Specific Overrides**

For Flatpak applications to access system themes:

```bash
# Give MCP server ability to set Flatpak overrides
flatpak override --user --filesystem=~/.themes:ro
flatpak override --user --filesystem=~/.icons:ro
flatpak override --user --filesystem=~/.local/share/plasma:ro
flatpak override --user --env=GTK_THEME=Win11
```

---

## 🔧 Method 7: **MCP Server Command-Line Arguments**

If you're launching the MCP server manually, pass permissions:

```bash
# Launch with extended permissions
mcp-server \
  --allow-commands "kwriteconfig6,qdbus6,plasma-apply-*,pacman,wget" \
  --allow-network \
  --allow-install \
  --config ~/.config/mcp/ricer-config.json
```

---

## 🔧 Method 8: **Docker/Podman Container with Mounted Config**

If running MCP server in a container:

```bash
# Run container with access to system configuration
podman run \
  --user $(id -u):$(id -g) \
  -v $HOME/.config:/home/user/.config:rw \
  -v $HOME/.local:/home/user/.local:rw \
  -v /usr/share/icons:/usr/share/icons:ro \
  -v /usr/share/themes:/usr/share/themes:ro \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  mcp-server-kde-ricer
```

---

## 🔧 Method 9: **Security Policy File**

Create a security policy for the MCP server:

```yaml
# ~/.config/mcp/security.yaml
version: 1
rules:
  - pattern: "kwriteconfig6 --file ~/.config/*"
    action: allow
    description: "Modify KDE config files"
  
  - pattern: "pacman -S --noconfirm *"
    action: ask
    description: "Install system packages (requires confirmation)"
  
  - pattern: "wget *"
    action: allow
    description: "Download theme assets"
  
  - pattern: "curl *"
    action: allow
    description: "Download theme assets"
  
  - pattern: "git clone *"
    action: allow
    description: "Clone theme repositories"
  
  - pattern: "plasmapkg2 --install *"
    action: allow
    description: "Install Plasma themes"
  
  - pattern: "rm -rf /*"
    action: deny
    description: "Dangerous operation - blocked"
```

---

## 🔧 Method 10: **MCP Server Implementation with Package Management**

Here's a complete example of an MCP server with download/install capabilities:

```python
#!/usr/bin/env python3
import os
import json
import subprocess
import tempfile
from pathlib import Path

class KDERicingMCPServer:
    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".config"
        self.local_dir = self.home / ".local/share"
        
    def download_file(self, url, destination):
        """Download a file using wget or curl"""
        try:
            # Try wget first
            subprocess.run(
                ["wget", "-O", destination, url],
                check=True,
                capture_output=True
            )
            return True
        except:
            # Fallback to curl
            try:
                subprocess.run(
                    ["curl", "-L", "-o", destination, url],
                    check=True,
                    capture_output=True
                )
                return True
            except:
                return False
    
    def install_aur_theme(self, theme_package):
        """Install theme from AUR using yay"""
        try:
            result = subprocess.run(
                ["yay", "-S", "--noconfirm", theme_package],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def install_flatpak_theme(self, theme_id):
        """Install Flatpak theme"""
        try:
            subprocess.run(
                ["flatpak", "install", "-y", theme_id],
                capture_output=True
            )
            return True
        except:
            return False
    
    def install_theme_from_github(self, repo_url, theme_type):
        """Install theme from GitHub repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clone repository
            subprocess.run(
                ["git", "clone", repo_url, tmpdir],
                capture_output=True
            )
            
            # Install based on theme type
            if theme_type == "plasma":
                dest = self.local_dir / "plasma/desktoptheme"
                dest.mkdir(parents=True, exist_ok=True)
                subprocess.run(["cp", "-r", f"{tmpdir}/*", dest])
            elif theme_type == "icons":
                dest = self.local_dir / "icons"
                dest.mkdir(parents=True, exist_ok=True)
                subprocess.run(["cp", "-r", f"{tmpdir}/*", dest])
            elif theme_type == "cursors":
                dest = self.local_dir / "icons"
                dest.mkdir(parents=True, exist_ok=True)
                subprocess.run(["cp", "-r", f"{tmpdir}/*", dest])
            
            return True
    
    def configure_theme(self, theme_config):
        """Apply theme configuration"""
        # Apply color scheme
        if "color_scheme" in theme_config:
            subprocess.run([
                "kwriteconfig6",
                "--file", f"{self.config_dir}/kdeglobals",
                "--group", "General",
                "--key", "ColorScheme",
                theme_config["color_scheme"]
            ])
        
        # Apply icon theme
        if "icon_theme" in theme_config:
            subprocess.run([
                "kwriteconfig6",
                "--file", f"{self.config_dir}/kdeglobals",
                "--group", "Icons",
                "--key", "Theme",
                theme_config["icon_theme"]
            ])
            subprocess.run(["kbuildsycoca6"])
        
        # Apply cursor theme
        if "cursor_theme" in theme_config:
            subprocess.run([
                "kwriteconfig6",
                "--file", f"{self.config_dir}/kcminputrc",
                "--group", "Mouse",
                "--key", "cursorTheme",
                theme_config["cursor_theme"]
            ])
            subprocess.run(["kapplymousetheme"])
        
        # Apply wallpaper
        if "wallpaper" in theme_config:
            subprocess.run([
                "plasma-apply-wallpaperimage",
                "--fill-mode", "preserveAspectCrop",
                theme_config["wallpaper"]
            ])
        
        # Apply GTK settings
        if "gtk_theme" in theme_config:
            gtk_config = self.config_dir / "gtk-3.0/settings.ini"
            gtk_config.parent.mkdir(exist_ok=True)
            with open(gtk_config, 'w') as f:
                f.write(f"""[Settings]
gtk-theme-name={theme_config['gtk_theme']}
gtk-icon-theme-name={theme_config.get('icon_theme', '')}
gtk-font-name={theme_config.get('font', 'Noto Sans 10')}
""")
        
        # Restart Plasma to apply
        subprocess.run(["kquitapp6", "plasmashell"])
        subprocess.run(["kstart6", "plasmashell"])
        
        return True

# MCP server would expose these methods to the AI
```

---

## 📋 Summary Table

| Capability | Method | Privilege Level |
|------------|--------|-----------------|
| **Modify KDE configs** | Write to `~/.config/` | User |
| **Install from AUR** | `yay -S` | Sudo or user (if configured) |
| **Install from Flatpak** | `flatpak install` | User |
| **Download themes** | `wget`, `curl` | User |
| **Clone from GitHub** | `git clone` | User |
| **Install Plasma themes** | `plasmapkg2` | User |
| **Install system packages** | `pacman -S` | Sudo required |
| **Apply configurations** | `qdbus6`, `kwriteconfig6` | User |

---

## 🚀 Quick Start for Your MCP Server

To give your MCP server download/install capabilities:

1. **Add to MCP config:**
```json
{
  "permissions": {
    "commands": ["pacman", "yay", "flatpak", "wget", "curl", "git"],
    "paths": ["~/.config", "~/.local/share"],
    "network": true
  }
}
```

2. **Set up sudoers (if needed):**
```bash
echo "your_username ALL=(ALL) NOPASSWD: /usr/bin/pacman" | sudo tee /etc/sudoers.d/mcp
```

3. **Launch with permissions:**
```bash
mcp-server --allow-network --allow-install --allow-file-write
```

With these configurations, your MCP server can fully automate KDE ricing, including downloading and installing themes from various sources!
