Here is the exact technical breakdown of the system changes Ricer will execute for each Accessibility Class in KDE Plasma 6.

---

## 1. The Aging Population (Motor & Visual Decline)

**Goal:** Maximize readability and reduce the need for high-precision mouse movements.

---

### \* Global UI Scaling (DPI)

Increase the entire desktop size by 125% or 150%.

- **Implementation:** On Plasma Wayland, this is best handled via `kscreen-doctor`.
- **Command:**

  ```
  kscreen-doctor output.1.scale.1.25
  ```

---

### \* Cursor Size

Increase the mouse pointer so it’s easier to track.

- **Implementation:** Edit the mouse input config.
- **Command:**

  ```
  kwriteconfig6 --file kcminputrc --group Mouse --key cursorSize 48
  ```

---

### \* Double-Click Interval

Older users often click slower. Increasing the allowed time between clicks prevents the system from registering a double-click as two single clicks.

- **Implementation:** Edit the global KDE input settings.
- **Command:**

  ```
  kwriteconfig6 --file kdeglobals --group KDE --key DoubleClickInterval 600
  ```

  (Default is usually 400ms).

---

### \* Single-Click to Open (Optional but recommended)

Replaces double-clicking entirely.

- **Implementation:**

  ```
  kwriteconfig6 --file kdeglobals --group KDE --key SingleClick true
  ```

---

### \* High Contrast Theme Option

Some older users need stronger contrast than Breeze Dark for better visibility.

- **Implementation:** Switch to Plasma High Contrast theme and adjust icon theme.
- **Commands:**

  ```
  lookandfeeltool --apply org.kde.highcontrast.desktop
  kwriteconfig6 --file kdeglobals --group General --key ColorScheme HighContrast
  kwriteconfig6 --file kdeglobals --group General --key IconTheme hicontrast
  ```

---

### \* Keyboard Accessibility

Motor decline affects not just mouse precision but keyboard control as well. These settings reduce accidental key presses and provide better keyboard control.

- **Implementation:** Enable sticky keys, slow keys, and bounce keys via input accessibility config.
- **Commands:**

  ```
  kwriteconfig6 --file kaccessrc --group Keyboard --key StickyKeys true
  kwriteconfig6 --file kaccessrc --group Keyboard --key StickyKeysLatch true
  kwriteconfig6 --file kaccessrc --group Keyboard --key SlowKeys true
  kwriteconfig6 --file kaccessrc --group Keyboard --key SlowKeysDelay 300
  kwriteconfig6 --file kaccessrc --group Keyboard --key BounceKeys true
  kwriteconfig6 --file kaccessrc --group Keyboard --key BounceKeysDelay 500
  kwriteconfig6 --file kaccessrc --group Keyboard --key RepeatRate 50
  kwriteconfig6 --file kaccessrc --group Keyboard --key RepeatDelay 500
  ```

---

### \* Larger Titlebars / Window Borders

Increases the grab area for resizing and moving windows, reducing the precision required.

- **Implementation:** Adjust KWin decoration settings.
- **Commands:**

  ```
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key BorderSize VeryLarge
  kwriteconfig6 --file kwinrc --group Windows --key BorderSnapZone 16
  ```

---

### \* Touchpad Sensitivity & Acceleration Control

Older users often struggle with pointer acceleration curves. Reducing sensitivity and acceleration helps prevent overshooting.

- **Implementation:** Configure touchpad input settings.
- **Commands:**

  ```
  kwriteconfig6 --file kcminputrc --group Touchpad --key Acceleration 0.5
  kwriteconfig6 --file kcminputrc --group Touchpad --key Speed 3
  kwriteconfig6 --file kcminputrc --group Touchpad --key Deceleration 1.5
  ```

---

## 2. Sensory-Sensitive & Neurodivergent Users (Low-Sensory Profile)

**Goal:** Eliminate sudden bright lights, jarring motion, and unexpected interruptions.

---

### \* Force Dark Mode

Instantly apply a dark global theme.

- **Implementation:** Use the Look-and-Feel tool.
- **Command:**

  ```
  lookandfeeltool --apply org.kde.breezedark.desktop
  ```

---

### \* Night Light (Blue Light Reduction)

Warm the screen temperature to reduce eye strain and migraine triggers.

- **Implementation:** Force KWin's Night Color to be constantly active.
- **Commands:**

  ```
  kwriteconfig6 --file kwinrc --group NightColor --key Active true
  kwriteconfig6 --file kwinrc --group NightColor --key Mode Constant
  ```

---

### \* Disable UI Animations

Turn off window minimizing effects, wobbly windows, and fading to prevent vestibular distress (motion sickness).

- **Implementation:** Set global animation duration to zero.
- **Command:**

  ```
  kwriteconfig6 --file kdeglobals --group KDE --key AnimationDurationFactor 0
  ```

---

### \* Enable "Do Not Disturb"

Silence all incoming notification popups and sounds.

- **Implementation:** Update the notification config and reload via D-Bus.
- **Command:**

  ```
  kwriteconfig6 --file plasmanotifyrc --group Notifications --key DoNotDisturb true
  ```

---

### \* Disable Cursor Blinking

Blinking text cursors can trigger discomfort, vestibular distress, and sensory overload.

- **Implementation:** Set cursor blink rate to zero.
- **Command:**

  ```
  kwriteconfig6 --file kdeglobals --group KDE --key CursorBlinkRate 0
  ```

---

### \* Disable Screen Flash on Notifications

Some themes flash subtly on notification arrival, which can be jarring for sensory-sensitive users.

- **Implementation:** Disable visual notification effects.
- **Command:**

  ```
  kwriteconfig6 --file plasmanotifyrc --group Notifications --key ShowPopups false
  ```

---

### \* Disable System Sounds

Not just notification sounds — event sounds from window actions, button clicks, and system events entirely.

- **Implementation:** Disable all system audio feedback.
- **Command:**

  ```
  kwriteconfig6 --file kdeglobals --group Sounds --key Enable false
  ```

---

### \* Disable Auto-Raise / Focus Stealing

Unexpected window popups and focus changes are stressful and disorienting.

- **Implementation:** Adjust KWin focus behavior.
- **Commands:**

  ```
  kwriteconfig6 --file kwinrc --group Windows --key AutoRaise false
  kwriteconfig6 --file kwinrc --group Windows --key FocusStealingPreventionLevel 4
  ```

---

### \* Static Wallpaper

No dynamic wallpapers or slideshow transitions; only a single static image.

- **Implementation:** Disable plasma wallpaper slideshow.
- **Command:**

  ```
  kwriteconfig6 --file plasmarc --group Wallpapers --key "org.kde.image/slideshow" "10000"
  ```

---

## 3. Users with Specific Deficits (Dyslexia & CVD)

**Goal:** Apply highly specific, medically supported visual aides.

---

### \* Dyslexia-Friendly Typography

Apply OpenDyslexic system-wide.

- **Implementation:** Assuming the font is installed, update kdeglobals.
- **Command:**

  ```
  kwriteconfig6 --file kdeglobals --group General --key font "OpenDyslexic,12,-1,5,50,0,0,0,0,0"
  ```

---

### \* Color Vision Deficiency (CVD) Correction

Shift the screen colors to make them distinguishable for Protanopia (red-blind) or Deuteranopia (green-blind).

- **Implementation:** KWin Plasma 6 has built-in shaders for this. You enable the KWin effect and specify the type.

- **Command 1 (Enable Effect):**

  ```
  kwriteconfig6 --file kwinrc --group Plugins --key colorblindnesscorrectionEnabled true
  ```

- **Command 2 (Set Type):**

  ```
  kwriteconfig6 --file kwinrc --group Effect-colorblindnesscorrection --key Type 0
  ```

  (0=Protanopia, 1=Deuteranopia, 2=Tritanopia)

---

### \* Increased Line Spacing

Dyslexia readability improves significantly with increased line spacing to prevent visual crowding.

- **Implementation:** Configure Qt and GTK font rendering with line spacing adjustments.
- **Commands:**

  ```
  mkdir -p ~/.config/fontconfig/conf.d
  echo '<?xml version="1.0"?><fontconfig><match target="font"><edit name="spacing" mode="assign"><const>100</const></edit></match></fontconfig>' > ~/.config/fontconfig/conf.d/dyslexia-spacing.conf
  kwriteconfig6 --file kdeglobals --group General --key "FixedFont" "Monospace,12,-1,5,50,0,0,0,0,0,Normal"
  ```

---

### \* Disable Subpixel Rendering

Subpixel rendering sometimes interferes with readability for dyslexic users.

- **Implementation:** Disable FreeType subpixel rendering.
- **Command:**

  ```
  echo '<?xml version="1.0"?><fontconfig><match target="font"><edit name="rgba" mode="assign"><const>none</const></edit></match></fontconfig>' > ~/.config/fontconfig/conf.d/no-subpixel.conf
  ```

---

### \* Per-Application Font Overrides

Some applications override system fonts. Qt and GTK environment variables can enforce consistency.

- **Implementation:** Set environment variables and create config overrides.
- **Commands:**

  ```
  echo 'export QT_FONT_DPI=96' >> ~/.profile
  echo 'export QT_QPA_PLATFORMTHEME=kde' >> ~/.profile
  mkdir -p ~/.config/gtk-3.0
  echo '[Settings]' > ~/.config/gtk-3.0/settings.ini
  echo 'gtk-font-name = OpenDyslexic 12' >> ~/.config/gtk-3.0/settings.ini
  ```

---

# 4. Advanced Accessibility Features (Currently Missing)

These are major accessibility layers not covered by the baseline system but critical for comprehensive support.

---

## 🧠 Screen Reader Support

Essential for severe visual impairment. Enables spoken feedback for all interface elements.

- **Implementation:** Enable Orca screen reader and configure Speech Dispatcher.
- **Commands:**

  ```
  kwriteconfig6 --file kaccessrc --group ScreenReader --key Active true
  kwriteconfig6 --file kaccessrc --group ScreenReader --key ScreenReaderEnabled true
  systemctl --user enable speech-dispatcher
  systemctl --user start speech-dispatcher
  ```

---

## 🔍 Magnifier / Zoom

Enables screen magnification for users with low vision.

- **Implementation:** Enable KWin magnifier effect.
- **Commands:**

  ```
  kwriteconfig6 --file kwinrc --group Plugins --key magnifierEnabled true
  kwriteconfig6 --file kwinrc --group Effect-magnifier --key Zoom 1.5
  ```

---

## 🖱 Click Assist

Automatic click detection after pointer has hovered in one location; useful for users with tremors who cannot hold clicks.

- **Implementation:** Enable dwell click in accessibility settings.
- **Commands:**

  ```
  kwriteconfig6 --file kaccessrc --group Mouse --key DwellClicking true
  kwriteconfig6 --file kaccessrc --group Mouse --key DwellTime 1000
  kwriteconfig6 --file kaccessrc --group Mouse --key DwellSimulatesSecondClick false
  ```

---

## 🕹 On-Screen Keyboard

Virtual keyboard for users with motor impairment who cannot use physical keyboards.

- **Implementation:** Configure Plasma's on-screen keyboard (Maliit).
- **Commands:**

  ```
  kwriteconfig6 --file kwinrc --group Plugins --key virtualkeyboardEnabled true
  kwriteconfig6 --file plasmarc --group General --key ShowOSD true
  ```

---

## 🔊 Text-to-Speech Integration

Enables reading of selected text and system notifications aloud.

- **Implementation:** Configure accessibility text-to-speech with Speech Dispatcher.
- **Commands:**

  ```
  kwriteconfig6 --file kaccessrc --group TextToSpeech --key Enabled true
  kwriteconfig6 --file kaccessrc --group TextToSpeech --key Module festival
  systemctl --user start speech-dispatcher
  ```

---

# 5. Architectural Considerations for Production Deployment

Your current design assumes each accessibility class is a static configuration batch. For a production-grade accessibility system, you'll need:

## Key Architectural Requirements

- **Profile Engine:** Modular system that detects and applies multi-layered configurations
- **Dependency Awareness:** Wayland vs X11 detection and conditional command execution
- **Session Restart Handling:** Properly restart KDE session after configuration changes
- **GTK Synchronization:** Not just KDE configs — ensure GTK applications respect accessibility settings
- **Hardware-Aware Decisions:** Detect touchscreen availability, laptop vs desktop, input device types

## Implementation Template

```python
class AccessibilityProfile:
    """Modular accessibility profile engine"""

    def __init__(self, profile_type):
        self.profile_type = profile_type
        self.commands = []
        self.post_sync_commands = [
            'qdbus6 org.kde.KWin /KWin reconfigure',
            'kquitapp6 plasmashell && sleep 2 && kstart6 plasmashell',
        ]

    def detect_session_type(self):
        """Determine Wayland vs X11"""
        return os.environ.get('XDG_SESSION_TYPE', 'x11')

    def execute_commands(self):
        """Execute all profile commands in sequence"""
        for cmd in self.commands:
            subprocess.run(cmd, shell=True)

        # Post-configuration sync
        for cmd in self.post_sync_commands:
            subprocess.run(cmd, shell=True)

    def apply_profile(self):
        """Main entry point for profile application"""
        self.execute_commands()
```

---

# 6. Production-Readiness Assessment

## Current Coverage vs. Production Requirements

✅ **Sufficient for:** Demo, proof-of-concept, educational purposes

❌ **Not sufficient for:** Production tool, enterprise deployment, medical-grade systems

## Gap Analysis

| Aspect                | Current      | Required                          |
| --------------------- | ------------ | --------------------------------- |
| Configuration Options | ~20          | ~50+                              |
| Framework Support     | KDE only     | KDE + GTK + Qt                    |
| Hardware Detection    | None         | Full device scanning              |
| Session Management    | Manual       | Fully automated                   |
| Testing Coverage      | None         | Multiple impairment scenarios     |
| Persistence           | Config files | Documented profile system         |
| Rollback Capability   | None         | Full configuration backup/restore |

---

# The Mandatory Final Step: State Synchronization

For almost all of the `kwriteconfig6` commands listed above, writing to the file isn't enough. Your backend Python execution engine must immediately tell KDE to re-read the configuration files so the changes appear instantly without requiring the user to reboot.

Every time Ricer finishes a batch of `kwriteconfig6` commands, it must run:

```
qdbus6 org.kde.KWin /KWin reconfigure
```
