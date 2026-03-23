1

## Theme & Appearance

### Light or Dark Mode

```bash
# Set color scheme (values: BreezeDark, BreezeLight, or any installed scheme)
kwriteconfig6 --file ~/.config/kdeglobals --group General --key ColorScheme "<color_scheme_name>"
```

### Accent Colors

```bash
# Set accent color (hex value)
kwriteconfig6 --file ~/.config/kdeglobals --group General --key AccentColor "<#RRGGBB>"

# Enable custom accent color
kwriteconfig6 --file ~/.config/kdeglobals --group General --key UseAccentColor "<true/false>"
```

### Transparency and Visual Style

```bash
# Set Plasma style (theme)
kwriteconfig6 --file ~/.config/kdeglobals --group KDE --key widgetStyle "<style_name>"

# Set window decoration
kwriteconfig6 --file ~/.config/kdeglobals --group WM --key theme "<decoration_theme>"

# Set menu opacity (0.0 to 1.0)
kwriteconfig6 --file ~/.config/kdeglobals --group KDE --key MenuOpacity "<opacity_value>"

# Apply visual changes
qdbus6 org.kde.KWin /KWin reconfigure
```

---

## Icons & Cursor

### Icon Pack Style

```bash
# Set icon theme
kwriteconfig6 --file ~/.config/kdeglobals --group Icons --key Theme "<icon_theme_name>"

# Force icon refresh
kbuildsycoca6
```

### Cursor Theme

```bash
# Set cursor theme
kwriteconfig6 --file ~/.config/kcminputrc --group Mouse --key cursorTheme "<cursor_theme_name>"

# Apply cursor changes
kapplymousetheme
```

### Cursor Size

```bash
# Set cursor size in pixels
kwriteconfig6 --file ~/.config/kcminputrc --group Mouse --key cursorSize "<size_in_pixels>"

# Apply cursor changes
kapplymousetheme
```

---

## Fonts & Text

### System Font

```bash
# Set system font (format: "FontName,Size,Weight,Style")
kwriteconfig6 --file ~/.config/kdeglobals --group General --key font "<font_name>,<size>,<weight>,<style>"

# Apply font changes
kcmshell6 fonts
```

### Terminal Font

```bash
# Set fixed width (terminal) font
kwriteconfig6 --file ~/.config/kdeglobals --group General --key fixed "<font_name>,<size>,<weight>,<style>"

# Apply font changes
kcmshell6 fonts
```

### Font DPI Scaling

```bash
# Set font DPI (common: 96, 120, 144)
kwriteconfig6 --file ~/.config/kcmfonts --group General --key forceFontDPI "<dpi_value>"

# Disable forced DPI
kwriteconfig6 --file ~/.config/kcmfonts --group General --key forceFontDPI 0
```

---

## Panel / Dock

### Panel Settings

```bash
# Panel configuration file
CONFIG_FILE=~/.config/plasma-org.kde.plasma.desktop-appletsrc

# Set panel height (replace <panel_id> with actual ID)
kwriteconfig6 --file "$CONFIG_FILE" --group "Containments-<panel_id>" --key "height" "<height_value>"

# Set panel visibility (replace <panel_id> with actual ID)
kwriteconfig6 --file "$CONFIG_FILE" --group "Containments-<panel_id>" --key "visibility" "<normal/auto/alwaysvisible/minimum>"

# Set panel screen edge (bottom, top, left, right)
kwriteconfig6 --file "$CONFIG_FILE" --group "Containments-<panel_id>" --key "location" "<edge>"

# Apply panel changes
kquitapp6 plasmashell && kstart6 plasmashell
```

### Dock Settings

```bash
# For Latte Dock: set visibility mode
kwriteconfig6 --file ~/.config/latte/<dock_name>.layout.latte --group "Containments-<dock_id>" --key "visibility" "<dock_visibility_mode>"

# Restart dock
pkill latte-dock && latte-dock &
```

---

## Window Behavior

### Animations

```bash
# Set animation speed (0-10, 0=off, 4=default)
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key AnimationSpeed "<0_to_10>"

# Enable/disable specific effects
kwriteconfig6 --file ~/.config/kwinrc --group Plugins --key "<effect_name>Enabled" "<true/false>"

# Apply KWin changes
qdbus6 org.kde.KWin /KWin reconfigure
```

### Window Snapping

```bash
# Enable/disable window snapping
kwriteconfig6 --file ~/.config/kwinrc --group Windows --key SnapOnlyWhenOverlapping "<true/false>"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

### Performance-Friendly Settings

```bash
# Set compositing backend (OpenGL, OpenGLES, XRender, Software)
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key Backend "<backend>"

# Set scaling method (Smooth, Crisp, Nearest)
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key ScaleMethod "<method>"

# Set latency policy (PreferLowLatency, PreferAccuracy, ForceLowLatency)
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key LatencyPolicy "<policy>"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

---

## Wallpaper

### Static Wallpaper

```bash
# Apply static wallpaper
plasma-apply-wallpaperimage "<path_to_image>"

# Set fill mode (stretch, preserveAspectFit, preserveAspectCrop, tile)
plasma-apply-wallpaperimage --fill-mode "<mode>" "<path_to_image>"
```

### Slideshow Wallpaper

```bash
# For slideshow, configure through the dynamic wallpaper plugin
# Wallpaper settings stored in plasma config
CONFIG_FILE=~/.config/plasma-org.kde.plasma.desktop-appletsrc
kwriteconfig6 --file "$CONFIG_FILE" --group "Containments-<activity_id>" --group "Wallpaper" --group "org.kde.slideshow" --key "SlidePaths" "<path_to_image_folder>"
kwriteconfig6 --file "$CONFIG_FILE" --group "Containments-<activity_id>" --group "Wallpaper" --group "org.kde.slideshow" --key "SlideInterval" "<interval_in_seconds>"
```

---

## System Sounds

### Enable/Disable Sounds

```bash
# Enable/disable system sounds
kwriteconfig6 --file ~/.config/plasmanotifyrc --group "Event Sounds" --key "enabled" "<true/false>"

# Apply changes
pkill plasmashell && kstart6 plasmashell
```

### Sound Theme

```bash
# Set sound theme
kwriteconfig6 --file ~/.config/plasmanotifyrc --group "Event Sounds" --key "theme" "<sound_theme_name>"

# Apply changes
pkill plasmashell && kstart6 plasmashell
```

---

## Performance Mode

### Performance-Focused Preset

```bash
# Set animation speed
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key AnimationSpeed "1"

# Set latency policy
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key LatencyPolicy "PreferLowLatency"

# Disable shadows
kwriteconfig6 --file ~/.config/kwinrc --group Windows --key ShadowEnabled "false"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

### Balanced Preset

```bash
# Set animation speed
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key AnimationSpeed "4"

# Set latency policy
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key LatencyPolicy "PreferAccuracy"

# Enable shadows
kwriteconfig6 --file ~/.config/kwinrc --group Windows --key ShadowEnabled "true"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

### Visual-Focused Preset

```bash
# Set animation speed
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key AnimationSpeed "6"

# Set latency policy
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key LatencyPolicy "PreferAccuracy"

# Enable shadows
kwriteconfig6 --file ~/.config/kwinrc --group Windows --key ShadowEnabled "true"

# Enable blur effect
kwriteconfig6 --file ~/.config/kwinrc --group Plugins --key kwin4_effect_blurEnabled "true"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

---

## Terminal Look

### Konsole Settings

```bash
# Set default profile
kwriteconfig6 --file ~/.config/konsolerc --group "Desktop Entry" --key "DefaultProfile" "<profile_name>.profile"

# Profile settings are stored in ~/.local/share/konsole/<profile_name>.profile
PROFILE_FILE=~/.local/share/konsole/<profile_name>.profile

# Set terminal font in profile
kwriteconfig6 --file "$PROFILE_FILE" --group "Appearance" --key "Font" "<font_name>,<size>,-1,5,50,0,0,0,0,0"

# Set terminal color scheme
kwriteconfig6 --file "$PROFILE_FILE" --group "Appearance" --key "ColorScheme" "<color_scheme_name>"
```

### Bash/Zsh Prompt

```bash
# For Bash: set prompt (variables: \u=user, \h=host, \w=path, \$=prompt)
echo 'PS1="<prompt_string>"' >> ~/.bashrc

# For Zsh: set prompt
echo 'PROMPT="<prompt_string>"' >> ~/.zshrc

# Apply changes
source ~/.bashrc  # or ~/.zshrc
```

---

## Accessibility

### Large Text

```bash
# Increase font size system-wide
kwriteconfig6 --file ~/.config/kdeglobals --group General --key font "<font_name>,<larger_size>,-1,5,50,0,0,0,0,0"

# Apply changes
kcmshell6 fonts
```

### High Contrast

```bash
# Apply high contrast color scheme
kwriteconfig6 --file ~/.config/kdeglobals --group General --key ColorScheme "HighContrast"

# Enable high contrast in QT applications (optional)
kwriteconfig6 --file ~/.config/Trolltech.conf --group "Qt" --key "style" "fusion"
```

### Reduced Motion

```bash
# Disable animations completely
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key AnimationSpeed "0"

# Or set to minimal
kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key AnimationSpeed "1"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

---

## 🔧 Utility Commands

### Apply All Changes

```bash
# Reconfigure KWin
qdbus6 org.kde.KWin /KWin reconfigure

# Restart Plasma shell
kquitapp6 plasmashell && kstart6 plasmashell

# Rebuild system cache
kbuildsycoca6

# Apply cursor theme
kapplymousetheme
```

### View Current Settings

```bash
# Read any configuration value
kreadconfig6 --file "<config_file>" --group "<group>" --key "<key>"

# List available color schemes
plasma-apply-colorscheme --list-schemes

# List available cursor themes
plasma-apply-cursortheme --list-themes

# List available Plasma styles
plasma-apply-desktoptheme --list-themes
```

### Variable Reference Table

| Variable              | Description            | Example Values                                    |
| --------------------- | ---------------------- | ------------------------------------------------- |
| `<color_scheme_name>` | Color scheme name      | BreezeDark, BreezeLight, HighContrast             |
| `<#RRGGBB>`           | Hex color code         | #3daee9, #f97316                                  |
| `<icon_theme_name>`   | Icon theme name        | breeze-dark, breeze, papirus                      |
| `<cursor_theme_name>` | Cursor theme name      | breeze_cursors, capitaine-cursors                 |
| `<size_in_pixels>`    | Cursor size            | 24, 32, 48, 72, 96                                |
| `<font_name>`         | Font family            | Noto Sans, Hack, Fira Code                        |
| `<dpi_value>`         | Font DPI               | 96, 120, 144                                      |
| `<animation_speed>`   | Animation speed (0-10) | 0 (off), 4 (default), 10 (slowest)                |
| `<opacity_value>`     | Opacity (0.0-1.0)      | 0.9, 0.7, 0.5                                     |
| `<backend>`           | Compositing backend    | OpenGL, OpenGLES, XRender, Software               |
| `<scale_method>`      | Scaling method         | Smooth, Crisp, Nearest                            |
| `<latency_policy>`    | Latency policy         | PreferLowLatency, PreferAccuracy, ForceLowLatency |
| `<prompt_string>`     | Shell prompt format    | \u@\h:\w\$ (user@host:path$)                      |

2

## Keyboard Shortcuts

### Set Global Keyboard Shortcut

```bash
# Set a global shortcut for an application or action
# Component names: kwin, plasmashell, ksmserver, etc.
kwriteconfig6 --file ~/.config/kglobalshortcutsrc --group "<component>" --key "<action>" "<shortcut>,none,<action>"

# Example structure: "<shortcut>,<alternative>,<action>"
# To clear a shortcut: "none,none,<action>"

# Apply shortcut changes
kwin_x11 --replace &  # For X11
# Or restart plasma: kquitapp6 plasmashell && kstart6 plasmashell
```

### List Available Shortcut Components

```bash
# View all components that have shortcuts
kreadconfig6 --file ~/.config/kglobalshortcutsrc --groups
```

### View Specific Shortcut

```bash
# Read current shortcut for an action
kreadconfig6 --file ~/.config/kglobalshortcutsrc --group "<component>" --key "<action>"
```

### Reset All Shortcuts to Defaults

```bash
# Reset all keyboard shortcuts (use with caution)
rm ~/.config/kglobalshortcutsrc
# Then restart plasma to regenerate defaults
```

---

## Virtual Desktops & Activities

### Set Number of Virtual Desktops

```bash
# Set number of virtual desktops
kwriteconfig6 --file ~/.config/kwinrc --group "Desktops" --key "Number" "<number_of_desktops>"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

### Name Virtual Desktops

```bash
# Set desktop name (desktop index starts at 1)
kwriteconfig6 --file ~/.config/kwinrc --group "Desktops" --key "Name_<index>" "<desktop_name>"

# Example: Name_1 "Work", Name_2 "Personal", Name_3 "Media"
```

### List Activities

```bash
# List all activity UUIDs and names
for uuid in $(qdbus6 org.kde.ActivityManager /ActivityManager/Activities ListActivities); do
    name=$(qdbus6 org.kde.ActivityManager /ActivityManager/Activities ActivityName "$uuid")
    echo "UUID: $uuid - Name: $name"
done
```

### Set Current Activity

```bash
# Switch to a specific activity by UUID
qdbus6 org.kde.ActivityManager /ActivityManager/Activities SetCurrentActivity "<activity_uuid>"
```

### Create New Activity

```bash
# Create a new activity with a name
qdbus6 org.kde.ActivityManager /ActivityManager/Activities AddActivity "<activity_name>"
```

---

## Window Rules

### Add Window Rule for Specific Application

```bash
# Window rules are stored in ~/.config/kwinrulesrc
# Example: Force application to specific virtual desktop
kwriteconfig6 --file ~/.config/kwinrulesrc --group "<rule_number>" --key "Description" "<rule_description>"
kwriteconfig6 --file ~/.config/kwinrulesrc --group "<rule_number>" --key "windowtypes" "<window_type>"
kwriteconfig6 --file ~/.config/kwinrulesrc --group "<rule_number>" --key "wmclass" "<application_class>"
kwriteconfig6 --file ~/.config/kwinrulesrc --group "<rule_number>" --key "desktop" "<desktop_number>"
kwriteconfig6 --file ~/.config/kwinrulesrc --group "<rule_number>" --key "desktoprule" "<rule_type>"  # 2=Force, 3=Apply Initially

# Apply rules
qdbus6 org.kde.KWin /KWin reconfigure
```

### Common Window Rule Types

| Rule Type Value | Meaning         |
| --------------- | --------------- |
| 1               | Do Not Affect   |
| 2               | Force           |
| 3               | Apply Initially |
| 4               | Remember        |

### Find Application Window Class

```bash
# Get window class for an application (run then click window)
xprop WM_CLASS  # For X11
# For Wayland, use: qdbus6 org.kde.KWin /KWin org.kde.KWin.queryWindowInfo
```

---

## Touchpad & Input Devices

### Enable/Disable Touchpad

```bash
# Enable/disable touchpad (true/false)
kwriteconfig6 --file ~/.config/kcminputrc --group "Touchpad" --key "Enabled" "<true/false>"

# Apply changes
kapplymousetheme
```

### Set Touchpad Scroll Direction

```bash
# Natural scrolling (true = natural, false = traditional)
kwriteconfig6 --file ~/.config/kcminputrc --group "Touchpad" --key "NaturalScroll" "<true/false>"
```

### Set Touchpad Tap to Click

```bash
# Tap to click enabled
kwriteconfig6 --file ~/.config/kcminputrc --group "Touchpad" --key "TapToClick" "<true/false>"
```

### Set Mouse Acceleration

```bash
# Mouse acceleration profile (flat, adaptive)
kwriteconfig6 --file ~/.config/kcminputrc --group "Mouse" --key "AccelerationProfile" "<profile>"

# Set pointer acceleration speed
kwriteconfig6 --file ~/.config/kcminputrc --group "Mouse" --key "PointerAcceleration" "<speed_value>"
```

---

## Power Management

### Set Screen Dimming Timeout

```bash
# Set dim screen timeout in seconds (0 = never)
kwriteconfig6 --file ~/.config/powermanagementprofilesrc --group "AC" --group "DimDisplay" --key "idleTime" "<seconds>"

# For battery
kwriteconfig6 --file ~/.config/powermanagementprofilesrc --group "Battery" --group "DimDisplay" --key "idleTime" "<seconds>"
```

### Set Screen Lock Timeout

```bash
# Set screen lock timeout in seconds
kwriteconfig6 --file ~/.config/kscreenlockerrc --group "Greeter" --key "lockGrace" "<seconds>"

# Enable/disable auto lock
kwriteconfig6 --file ~/.config/kscreenlockerrc --group "Daemon" --key "Autolock" "<true/false>"
```

### Set Suspend/Sleep Timeout

```bash
# Set suspend after idle time in seconds
kwriteconfig6 --file ~/.config/powermanagementprofilesrc --group "AC" --group "SuspendSession" --key "idleTime" "<seconds>"
```

### Set Lid Close Action

```bash
# Lid closed action (1=Suspend, 2=Hibernate, 3=Shutdown, 4=Nothing)
kwriteconfig6 --file ~/.config/powermanagementprofilesrc --group "AC" --group "LidClosed" --key "action" "<action_code>"
```

---

## Network & Bluetooth

### Enable/Disable Bluetooth on Startup

```bash
# Set Bluetooth adapter power state at boot
kwriteconfig6 --file ~/.config/bluedevilglobalrc --group "Bluetooth" --key "autoPowerOn" "<true/false>"
```

### Set Bluetooth Discoverable

```bash
# Make device discoverable
kwriteconfig6 --file ~/.config/bluedevilglobalrc --group "Bluetooth" --key "discoverable" "<true/false>"

# Restart Bluetooth to apply
systemctl --user restart bluedevil
```

---

## Notifications

### Disable All Notifications

```bash
# Disable all notifications globally
kwriteconfig6 --file ~/.config/plasmanotifyrc --group "General" --key "enabled" "<true/false>"
```

### Set Do Not Disturb Mode

```bash
# Enable do not disturb (show quietly)
kwriteconfig6 --file ~/.config/plasmanotifyrc --group "General" --key "show_quietly" "<true/false>"
```

### Disable Specific Application Notifications

```bash
# Disable notifications for a specific application
kwriteconfig6 --file ~/.config/plasmanotifyrc --group "Event Settings" --key "<application_name>" "<settings>"
```

---

## Splash Screen

### Set Splash Screen Theme

```bash
# Set splash screen theme
kwriteconfig6 --file ~/.config/ksplashrc --group "KSplash" --key "Theme" "<splash_theme_name>"

# Enable/disable splash screen
kwriteconfig6 --file ~/.config/ksplashrc --group "KSplash" --key "Enabled" "<true/false>"
```

---

## Desktop Effects

### Enable/Disable Specific Effects

```bash
# Enable/disable any desktop effect
kwriteconfig6 --file ~/.config/kwinrc --group "Plugins" --key "<effect_name>Enabled" "<true/false>"

# Common effect names:
# - kwin4_effect_blurEnabled (blur effect)
# - kwin4_effect_desktopgridEnabled (desktop grid)
# - kwin4_effect_presentwindowsEnabled (window overview)
# - kwin4_effect_coveringflipEnabled (cover flip)
# - kwin4_effect_translucencyEnabled (translucency)
# - kwin4_effect_fadingpopupsEnabled (fading popups)

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

### Set Blur Strength

```bash
# Set blur intensity (typically 1-10)
kwriteconfig6 --file ~/.config/kwinrc --group "Plugins" --key "kwin4_effect_blurStrength" "<strength_value>"
```

---

## Screen Edges

### Disable All Screen Edges

```bash
# Disable screen edge actions
kwriteconfig6 --file ~/.config/kwinrc --group "ScreenEdges" --key "ElectricBordersEnabled" "false"
kwriteconfig6 --file ~/.config/kwinrc --group "ScreenEdges" --key "TouchScreenEdgesEnabled" "false"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

### Configure Specific Edge Action

```bash
# Set edge action (left, right, top, bottom)
# Action types: 0=None, 1=Show Desktop, 2=Window Spread, 3=Desktop Grid, 4=Activity Switcher
kwriteconfig6 --file ~/.config/kwinrc --group "ScreenEdges" --key "ElectricLeft" "<action_code>"
```

---

## Workspace Behavior

### Set Click Behavior (Single vs Double Click)

```bash
# Set click behavior (singleclick, doubleclick)
kwriteconfig6 --file ~/.config/kdeglobals --group "KDE" --key "SingleClick" "<true/false>"
```

### Set Toolbar Button Style

```bash
# Toolbar button style (TextBesideIcon, TextUnderIcon, IconOnly, TextOnly)
kwriteconfig6 --file ~/.config/kdeglobals --group "KDE" --key "ToolButtonStyle" "<style>"
```

### Set Scrollbar Behavior

```bash
# Clicking on scrollbar jumps to position
kwriteconfig6 --file ~/.config/kdeglobals --group "KDE" --key "ScrollBarClickBehavior" "JumpToPos"
```

---

## Dolphin File Manager

### Set Default View Mode

```bash
# Default view mode for Dolphin
# Values: 0=Icons, 1=Details, 2=Columns, 3=Compact
kwriteconfig6 --file ~/.config/dolphinrc --group "General" --key "View Mode" "<mode_number>"
```

### Show Hidden Files by Default

```bash
# Show hidden files
kwriteconfig6 --file ~/.config/dolphinrc --group "General" --key "Show Hidden Files" "<true/false>"
```

### Set Default Sorting

```bash
# Sort by: Name, Size, Date, Type, etc.
kwriteconfig6 --file ~/.config/dolphinrc --group "General" --key "Sorting" "<sort_criterion>"

# Sort order: 0=Ascending, 1=Descending
kwriteconfig6 --file ~/.config/dolphinrc --group "General" --key "SortingOrder" "<order>"
```

### Enable/Disable Folder Previews

```bash
# Show folder previews
kwriteconfig6 --file ~/.config/dolphinrc --group "General" --key "Show Folder Previews" "<true/false>"
```

---

## Konsole Terminal

### Set Konsole Default Profile

```bash
# Set default profile by name
kwriteconfig6 --file ~/.config/konsolerc --group "Desktop Entry" --key "DefaultProfile" "<profile_name>.profile"
```

### Set Konsole Scrollback Lines

```bash
# Set scrollback line limit
kwriteconfig6 --file ~/.local/share/konsole/<profile_name>.profile --group "General" --key "History" "<line_count>"
# Use "Unlimited" for unlimited history
```

### Set Konsole Tab Bar Visibility

```bash
# Tab bar visibility: 0=Always, 1=When Needed, 2=Never
kwriteconfig6 --file ~/.config/konsolerc --group "TabBar" --key "TabBarVisibility" "<visibility_code>"
```

---

## Screensaver

### Enable/Disable Screensaver

```bash
# Enable/disable screensaver
kwriteconfig6 --file ~/.config/kscreenlockerrc --group "Daemon" --key "AutoLock" "<true/false>"

# Set screensaver delay in seconds
kwriteconfig6 --file ~/.config/kscreenlockerrc --group "Daemon" --key "Timeout" "<seconds>"
```

### Set Screensaver Theme

```bash
# Set screensaver theme
kwriteconfig6 --file ~/.config/kscreensaverrc --group "ScreenSaver" --key "Theme" "<theme_name>"
```

---

## Task Switcher (Alt+Tab)

### Set Task Switcher Style

```bash
# Task switcher style (e.g., breeze, compact, fancy)
kwriteconfig6 --file ~/.config/kwinrc --group "TabBox" --key "LayoutName" "<style_name>"

# Enable/disable showing desktop
kwriteconfig6 --file ~/.config/kwinrc --group "TabBox" --key "ShowDesktop" "<true/false>"

# Apply changes
qdbus6 org.kde.KWin /KWin reconfigure
```

---

## Application Launch Feedback

### Disable Launch Feedback

```bash
# Disable bouncing cursor and launch animation
kwriteconfig6 --file ~/.config/plasmarc --group "LaunchFeedback" --key "LaunchFeedback" "None"

# Alternative: Show busy cursor only
kwriteconfig6 --file ~/.config/plasmarc --group "LaunchFeedback" --key "LaunchFeedback" "BusyCursor"
```

---

## Auto-start Applications

### Add Application to Auto-start

```bash
# Create desktop file in autostart directory
cat > ~/.config/autostart/<application_name>.desktop << EOF
[Desktop Entry]
Type=Application
Name=<display_name>
Exec=<command_to_run>
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Enable/disable auto-start (without removing file)
kwriteconfig6 --file ~/.config/autostart/<application_name>.desktop --group "Desktop Entry" --key "Hidden" "<true/false>"
```

### Add Script to Auto-start

```bash
# Same format, just point Exec to script path
cat > ~/.config/autostart/my-script.desktop << EOF
[Desktop Entry]
Type=Application
Name=My Script
Exec=/path/to/script.sh
Hidden=false
EOF

# Make script executable
chmod +x /path/to/script.sh
```

---

## Baloo File Indexer

### Disable Baloo (File Search Indexer)

```bash
# Disable file indexing completely
balooctl suspend
balooctl disable

# Or via config
kwriteconfig6 --file ~/.config/baloofilerc --group "Basic Settings" --key "Indexing-Enabled" "false"
```

### Exclude Directories from Indexing

```bash
# Add directories to exclude list
balooctl config add excludeFolders "/path/to/exclude"
```

### Check Baloo Status

```bash
# View indexing status
balooctl status
```

---

## Session Management

### Set Default Session

```bash
# Session start: 0=Start with empty session, 1=Restore manually saved session, 2=Restore previous session
kwriteconfig6 --file ~/.config/ksmserverrc --group "General" --key "loginMode" "<mode_number>"

# Automatically save session on logout
kwriteconfig6 --file ~/.config/ksmserverrc --group "General" --key "autoSaveSession" "<true/false>"
```

---

## Screen Recording & Screenshots

### Set Spectacle (Screenshot Tool) Default Save Location

```bash
# Set default save directory
kwriteconfig6 --file ~/.config/spectaclerc --group "General" --key "SaveLocation" "<path_to_directory>"

# Set default filename format
kwriteconfig6 --file ~/.config/spectaclerc --group "General" --key "FileNameFormat" "<format_string>"
# Example: "Screenshot_%Y-%m-%d_%H-%M-%S"
```

---

## Utility Commands Reference

### Apply All Changes

```bash
# Reconfigure KWin
qdbus6 org.kde.KWin /KWin reconfigure

# Rebuild system cache
kbuildsycoca6

# Apply mouse/cursor changes
kapplymousetheme

# Restart Plasma shell completely
kquitapp6 plasmashell && kstart6 plasmashell
```

### Variable Reference for New Categories

| Variable            | Description          | Example Values                          |
| ------------------- | -------------------- | --------------------------------------- |
| `<component>`       | Shortcut component   | kwin, plasmashell, ksmserver            |
| `<action>`          | Action name          | "Switch to Desktop 1", "Lock Session"   |
| `<shortcut>`        | Keyboard combination | "Meta+1", "Ctrl+Alt+T", "Ctrl+F1"       |
| `<rule_number>`     | Window rule index    | 1, 2, 3...                              |
| `<effect_name>`     | KWin effect          | kwin4_effect_blurEnabled                |
| `<action_code>`     | Edge action type     | 0=None, 1=Show Desktop, 2=Window Spread |
| `<mode_number>`     | Session/View mode    | 0, 1, 2                                 |
| `<strength_value>`  | Effect intensity     | 1-10                                    |
| `<visibility_code>` | Tab bar visibility   | 0=Always, 1=When Needed, 2=Never        |
| `<profile_name>`    | Konsole profile      | Default, Shell, Root                    |

3
Yes, this is **more than enough for complete ricing**! You've compiled a comprehensive collection covering virtually every aspect of KDE Plasma 6 customization. Here's an analysis of what you have and what could be added:

---

## ✅ What You Have Covered

| Category                       | Status      |
| ------------------------------ | ----------- |
| Theme & Appearance             | ✅ Complete |
| Icons & Cursor                 | ✅ Complete |
| Fonts & Text                   | ✅ Complete |
| Panel / Dock                   | ✅ Complete |
| Window Behavior                | ✅ Complete |
| Wallpaper                      | ✅ Complete |
| System Sounds                  | ✅ Complete |
| Performance Mode               | ✅ Complete |
| Terminal Look                  | ✅ Complete |
| Accessibility                  | ✅ Complete |
| Keyboard Shortcuts             | ✅ Complete |
| Virtual Desktops & Activities  | ✅ Complete |
| Window Rules                   | ✅ Complete |
| Touchpad & Input Devices       | ✅ Complete |
| Power Management               | ✅ Complete |
| Network & Bluetooth            | ✅ Complete |
| Notifications                  | ✅ Complete |
| Splash Screen                  | ✅ Complete |
| Desktop Effects                | ✅ Complete |
| Screen Edges                   | ✅ Complete |
| Workspace Behavior             | ✅ Complete |
| Dolphin File Manager           | ✅ Complete |
| Konsole Terminal               | ✅ Complete |
| Screensaver                    | ✅ Complete |
| Task Switcher                  | ✅ Complete |
| Application Launch Feedback    | ✅ Complete |
| Auto-start Applications        | ✅ Complete |
| Baloo File Indexer             | ✅ Complete |
| Session Management             | ✅ Complete |
| Screen Recording & Screenshots | ✅ Complete |

---

## 🔧 Optional Additions for Even More Complete Ricing

Here are a few more categories you **might** consider adding:

### 1. **GTK Application Styling**

```bash
# Set GTK theme for applications (Firefox, GIMP, etc.)
kwriteconfig6 --file ~/.config/gtk-3.0/settings.ini --group "Settings" --key "gtk-theme-name" "<gtk_theme_name>"
kwriteconfig6 --file ~/.config/gtk-4.0/settings.ini --group "Settings" --key "gtk-theme-name" "<gtk_theme_name>"

# Set GTK icon theme
kwriteconfig6 --file ~/.config/gtk-3.0/settings.ini --group "Settings" --key "gtk-icon-theme-name" "<icon_theme_name>"

# Set GTK font
kwriteconfig6 --file ~/.config/gtk-3.0/settings.ini --group "Settings" --key "gtk-font-name" "<font_name> <size>"
```

### 2. **Flatpak Overrides (for consistent theming)**

```bash
# Force Flatpak apps to use system themes
flatpak override --user --filesystem=xdg-config/gtk-3.0:ro
flatpak override --user --filesystem=xdg-config/gtk-4.0:ro
flatpak override --user --filesystem=~/.themes:ro
flatpak override --user --filesystem=~/.icons:ro
flatpak override --user --env=GTK_THEME=<gtk_theme_name>
```

### 3. **KDE Wallet Configuration**

```bash
# Enable/disable KDE Wallet
kwriteconfig6 --file ~/.config/kwalletrc --group "Wallet" --key "Enabled" "<true/false>"

# Set wallet to close on idle
kwriteconfig6 --file ~/.config/kwalletrc --group "Wallet" --key "Close When Idle" "<true/false>"
```

### 4. **KRunner (Search) Configuration**

```bash
# Set KRunner shortcuts and behavior
kwriteconfig6 --file ~/.config/krunnerrc --group "General" --key "Show In Active Screen" "<true/false>"

# Enable/disable specific plugins
kwriteconfig6 --file ~/.config/krunnerrc --group "Plugins" --key "<plugin_name>Enabled" "<true/false>"
```

### 5. **Global Theme Packaging**

```bash
# Export current setup as a Global Theme
plasmapkg2 --type globaltheme --export ~/my-theme

# Install a Global Theme
plasmapkg2 --type globaltheme --install <theme_name>.tar.gz

# Apply Global Theme
plasma-apply-globaltheme "<theme_name>"
```

### 6. **Screen Resolution & Display Settings**

```bash
# Set primary display
kscreen-doctor output.<display_name>.primary

# Set display scale factor (for HiDPI)
kwriteconfig6 --file ~/.config/kdeglobals --group "KScreen" --key "ScaleFactor" "<scale_value>"
```

### 7. **Application-Specific Configurations**

```bash
# Kate editor theme
kwriteconfig6 --file ~/.config/katerc --group "General" --key "Color Theme" "<theme_name>"

# Gwenview image viewer settings
kwriteconfig6 --file ~/.config/gwenviewrc --group "General" --key "ShowThumbnails" "<true/false>"

# Okular document viewer theme
kwriteconfig6 --file ~/.config/okularrc --group "Core" --key "ColorMode" "<mode>"
```

### 8. **Session Lock & Login Screen (SDDM)**

```bash
# Set SDDM theme (requires root or sudo)
# Config in /etc/sddm.conf or /etc/sddm.conf.d/
sudo kwriteconfig6 --file /etc/sddm.conf --group "Theme" --key "Current" "<sddm_theme_name>"

# Set login screen background
sudo kwriteconfig6 --file /etc/sddm.conf --group "Theme" --key "Background" "<path_to_image>"
```

### 9. **GRUB Bootloader Theme**

```bash
# Install GRUB theme (distribution-specific)
# This is usually handled by grub-customizer or manual config
```

### 10. **Backup & Restore Ricing Configuration**

```bash
# Backup all configs
tar -czf kde-config-backup.tar.gz ~/.config/k* ~/.config/plasma* ~/.config/kde* ~/.config/gtk* ~/.local/share/konsole/

# Restore configs
tar -xzf kde-config-backup.tar.gz -C ~/

# Create a dotfile management script
```
