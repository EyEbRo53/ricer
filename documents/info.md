How it works

Plasma Shell exposes objects via DBus, like /PlasmaShell.

You can call the evaluateScript method on it.

Inside the script, panels() returns all panels currently loaded.

Setting panel.location = "right" tells Plasma to move the panel in memory immediately.

Plasma redraws the panel on the new side without relying on config files.

Why DBus works better than editing config

Config changes (desktop-appletsrc) are only applied when Plasma reads the file, which may not happen immediately.

In VirtualBox or Plasma 6, config caching or per-screen settings can prevent config changes from taking effect.

DBus communicates directly with the running shell, bypassing caches.

----->We wrote a script to change the position of the panel. All approaches except for dbus failed. The reason for dbus working is listed above.
