import os
import json
import subprocess

WIDGET_ID = "com.example.perspectiveicons"

BASE_DIR = os.path.expanduser(f"~/.local/share/plasma/plasmoids/{WIDGET_ID}")

UI_DIR = os.path.join(BASE_DIR, "contents/ui")


# -----------------------------
# Step 1: Create Folder Layout
# -----------------------------
def create_structure():
    os.makedirs(UI_DIR, exist_ok=True)
    print("✓ Widget folders created")


# -----------------------------
# Step 2: Write metadata.json
# -----------------------------
def write_metadata():
    metadata = {
        "KPlugin": {
            "Id": WIDGET_ID,
            "Name": "3D Perspective Desktop Icons",
            "Description": "Perspective icon navigation demo for Plasma 6",
            "Version": "1.0",
            "License": "GPL",
            "Category": "Desktop",
        },
        "X-Plasma-API": "declarativeappletscript",
        "KPackageStructure": "Plasma/Applet",
    }

    path = os.path.join(BASE_DIR, "metadata.json")
    with open(path, "w") as f:
        json.dump(metadata, f, indent=4)

    print("✓ Plasma 6 metadata.json written")


# -----------------------------
# Step 3: Write main.qml
# -----------------------------
def write_qml():
    qml_code = r"""
import QtQuick 2.15

Item {
    width: 800
    height: 600
    focus: true

    property int selectedIndex: 0
    property var icons: ["Firefox", "Dolphin", "Terminal", "Settings"]

    Keys.onPressed: (event) => {
        if (event.key === Qt.Key_Right)
            selectedIndex = (selectedIndex + 1) % icons.length

        if (event.key === Qt.Key_Left)
            selectedIndex = (selectedIndex - 1 + icons.length) % icons.length
    }

    Rectangle {
        anchors.fill: parent
        color: "#111"
    }

    Repeater {
        model: icons.length

        delegate: Item {
            property real depth: index * 0.18

            x: 100 + depth * 250
            y: 200 + depth * 120
            scale: 1.0 - depth * 0.35

            Rectangle {
                width: 120
                height: 60
                radius: 12

                border.width: index === selectedIndex ? 3 : 1
                border.color: index === selectedIndex ? "cyan" : "gray"

                color: "#222"

                Text {
                    anchors.centerIn: parent
                    text: icons[index]
                    color: "white"
                }
            }
        }
    }
}
"""

    path = os.path.join(UI_DIR, "main.qml")
    with open(path, "w") as f:
        f.write(qml_code)

    print("✓ main.qml written")


# -----------------------------
# Step 4: Add Widget via gdbus
# -----------------------------
def add_widget_to_desktop():
    print("Adding widget to desktop via DBus...")

    js_script = f"""
    var desktops = desktops();
    for (var i = 0; i < desktops.length; i++) {{
        desktops[i].addWidget("{WIDGET_ID}");
    }}
    """

    subprocess.run(
        [
            "gdbus",
            "call",
            "--session",
            "--dest",
            "org.kde.plasmashell",
            "--object-path",
            "/PlasmaShell",
            "--method",
            "org.kde.PlasmaShell.evaluateScript",
            js_script,
        ]
    )

    print("✓ Widget added to desktop (no restart)")


# -----------------------------
# Main Installer
# -----------------------------
if __name__ == "__main__":
    create_structure()
    write_metadata()
    write_qml()
    add_widget_to_desktop()

    print("\nDONE ✅ Widget installed + applied!")
