"""Stage a wallpaper change (display — applies live via DBus)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_wallpaper(path: str) -> str:
        """Stage a wallpaper change.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_wallpaper
        Change type: display (applies live via DBus/qdbus)

        Args:
            path: Absolute file path to the wallpaper image.
                  Supported formats: .jpg, .jpeg, .png, .bmp, .webp

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json
        import os

        filename = os.path.basename(path)
        receipt = changeset.add(
            description=f"Change wallpaper to {filename}",
            change_type="display",
            script="set_wallpaper",
            parameters={"path": path},
        )
        return json.dumps(receipt, indent=2)
