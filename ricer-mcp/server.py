import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from changeset import changeset
from provider_runtime import ensure_provider_paths

# Import our low-level read/write logic
from providers.kde_plasma_6.temp.read import get_config_value
from providers.kde_plasma_6.temp.write import stage_kde_change

# Initialize FastMCP
mcp = FastMCP("ricer-mcp")

def bootstrap_metadata_features():
    """Dynamically registers tools and resources from accessibility_meta.json"""
    meta_path = Path("providers/kde-plasma-6/temp/accessibility_meta.json")
    
    if not meta_path.exists():
        print(f"⚠️ Metadata not found at {meta_path}")
        return

    with open(meta_path, "r") as f:
        categories = json.load(f)

    for category_name, settings in categories.items():
        for setting_id, info in settings.items():
            
            # Create a closure to capture the current setting's metadata
            def create_tool(s_id, s_info):
                @mcp.tool(name=f"set_{s_id}")
                def tool_func(value: str, reason: str) -> dict:
                    # Access s_info inside the closure
                    return stage_kde_change(
                        file=s_info['file'],
                        group=s_info['group'],
                        key=s_info['key'],
                        value=value,
                        description=f"[{category_name}] {reason}"
                    )
                # Set docstring dynamically for the LLM
                tool_func.__doc__ = f"Update {s_id}. {s_info['description']}"

            def create_resource(s_id, s_info):
                @mcp.resource(uri=f"config://{s_id}")
                def resource_func() -> str:
                    val = get_config_value(s_info['file'], s_info['group'], s_info['key'])
                    return json.dumps({
                        "setting": s_id,
                        "current_value": val,
                        "meta": s_info
                    })

            # Register them
            create_tool(setting_id, info)
            create_resource(setting_id, info)

# 1. Load dynamic features
bootstrap_metadata_features()

# 2. Add the Control Tool (The "Apply" button)
@mcp.tool()
def apply_all_staged_changes() -> str:
    """Executes all staged changes in the changeset and clears it."""
    staged = changeset.staged()
    if not staged:
        return "No changes staged."
    
    import subprocess
    for entry in staged:
        try:
            subprocess.run(entry.script, shell=True, check=True)
            changeset.mark_applied(entry.order)
        except Exception as e:
            return f"Error applying {entry.description}: {str(e)}"
    
    # Refresh KWin/Plasma so changes are visible immediately
    subprocess.run("qdbus6 org.kde.KWin /KWin reconfigure", shell=True)
    
    return f"Successfully applied {len(staged)} changes."

if __name__ == "__main__":
    mcp.run()