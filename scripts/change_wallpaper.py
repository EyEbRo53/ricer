import os
import subprocess

# ----------------------------
# HARDCODED WALLPAPER FOLDER
# ----------------------------
WALLPAPER_DIR = "/home/eyebro/Documents/FYP/ricer/wallpapers"
# Supported formats
SUPPORTED_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def get_wallpapers():
    """Load all images from folder"""
    files = sorted(
        [f for f in os.listdir(WALLPAPER_DIR) if f.lower().endswith(SUPPORTED_EXT)]
    )
    return [os.path.join(WALLPAPER_DIR, f) for f in files]


def set_wallpaper(image_path):
    """Change KDE Plasma wallpaper using DBus"""
    script = f"""
    var allDesktops = desktops();
    for (i=0; i<allDesktops.length; i++) {{
        d = allDesktops[i];
        d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        d.writeConfig("Image", "file://{image_path}");
    }}
    """

    subprocess.run(
        [
            "qdbus",
            "org.kde.plasmashell",
            "/PlasmaShell",
            "org.kde.PlasmaShell.evaluateScript",
            script,
        ]
    )


def main():
    wallpapers = get_wallpapers()

    if not wallpapers:
        print("❌ No wallpapers found in folder!")
        return

    index = 0
    print("✅ Wallpaper changer started.")
    print("Press ENTER to change wallpaper. Ctrl+C to exit.\n")

    while True:
        input("➡ Press Enter...")

        image = wallpapers[index]
        print(f"🎨 Setting wallpaper: {os.path.basename(image)}")

        set_wallpaper(image)

        index = (index + 1) % len(wallpapers)


if __name__ == "__main__":
    main()
