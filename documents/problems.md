if changes are not visible command Wayland compositor to replace itself with
kwin_wayland --replace &
Warning: restarts the environment, current applications will crash

### live changes not possible in input settings

this is a Plasma 6 Wayland quirk rooted in how input vs. display settings are handled. It’s subtle but logical once you break it down:

1️⃣ Global Scaling vs Cursor Size

Global scaling (like KWin’s ScaleFactor) affects all outputs, windows, and GUI elements.

Wayland actively queries this value from KWin whenever a window is drawn.

Plasma exposes a live IPC channel for scaling, so kwriteconfig6 + qdbus org.kde.KWin /KWin reloadConfig immediately propagates scaling changes.

Every application asks KWin “what’s my scale factor?” dynamically — no caching per cursor, no deep internal state.

Result: changes appear instantly.

2️⃣ Cursor Size

The cursor is different:

On Wayland, the cursor is rendered by the compositor (KWin) per output and per seat.

Cursor size is cached in the compositor’s seat/input layer and not polled dynamically from kcminputrc.

Changing the config file only updates Plasma’s settings file, but KWin does not automatically re-read the cursor size from disk.

plasma-apply-cursortheme only reloads the theme, not the size parameter.

Result: cursor size changes require a compositor/seat refresh, which currently has no clean live CLI on Plasma Wayland. That’s why logout/login is the usual reliable method.

### restarting kwin and kded6

these are the commands to kill and restart kded6 (plasma 6 daemon)
killall kded6 # stops the current daemon
/usr/bin/kded6 & # starts a new instance
