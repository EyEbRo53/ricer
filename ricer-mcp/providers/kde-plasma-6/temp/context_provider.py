import json
from pathlib import Path

def get_accessibility_context():
    """
    Loads the objective metadata to provide the LLM with 
    technical context for available accessibility classes.
    """
    meta_path = Path("accessibility_meta.json")
    
    if not meta_path.exists():
        return {"error": "Metadata file missing."}
        
    with open(meta_path, "r") as f:
        metadata = json.load(f)
        
    # We return the data structured for the LLM's system prompt or tool context
    return {
        "role": "system_metadata",
        "content": metadata,
        "instructions": "Use this metadata to identify the correct file/group/key for requested system changes. Stage changes via write.py."
    }