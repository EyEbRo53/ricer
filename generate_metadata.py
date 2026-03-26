# import os
# import json
# import configparser
# from pathlib import Path

# # Files we want to index for the MCP server
# TARGET_FILES = [
#     "kdeglobals",
#     "kwinrc",
#     "kcminputrc",
#     "plasmarc",
#     "kcmfonts"
# ]

# def infer_type(value):
#     """Simple inference to help the LLM understand data constraints."""
#     if value.lower() in ['true', 'false']:
#         return "boolean"
#     try:
#         int(value)
#         return "integer"
#     except ValueError:
#         try:
#             float(value)
#             return "float"
#         except ValueError:
#             return "string"

# def generate_metadata():
#     config_path = Path.home() / ".config"
#     mcp_dictionary = {}

#     for file_name in TARGET_FILES:
#         file_path = config_path / file_name
#         if not file_path.exists():
#             continue

#         # KConfig files sometimes have no spaces around '=', 
#         # and allow backslashes, so we use a permissive configparser
#         config = configparser.ConfigParser(interpolation=None, strict=False)
#         try:
#             config.read(file_path)
            
#             file_meta = {}
#             for section in config.sections():
#                 section_meta = {}
#                 for key, value in config.items(section):
#                     section_meta[key] = {
#                         "current_value": value,
#                         "type": infer_type(value),
#                         "description": f"Key '{key}' found in [{section}] of {file_name}"
#                     }
#                 file_meta[section] = section_meta
            
#             mcp_dictionary[file_name] = file_meta
#         except Exception as e:
#             print(f"Error parsing {file_name}: {e}")

#     return mcp_dictionary

# if __name__ == "__main__":
#     metadata = generate_metadata()
    
#     # Save to a JSON file for your MCP server to consume
#     output_file = "kde_settings_metadata.json"
#     with open(output_file, "w") as f:
#         json.dump(metadata, f, indent=4)
    
#     print(f"Successfully generated metadata for {len(metadata)} files.")
#     print(f"Output saved to: {os.path.abspath(output_file)}")


# import xml.etree.ElementTree as ET
# import glob
# import json
# import os

# def parse_all_kcfg():
#     mcp_master_schema = {}
    
#     # Search for all KDE configuration definition files
#     kcfg_path = "/usr/share/config.kcfg/*.kcfg"
    
#     for kcfg_file in glob.glob(kcfg_path):
#         try:
#             tree = ET.parse(kcfg_file)
#             root = tree.getroot()
            
#             # The 'kcfg' tag usually tells us which .rc file it belongs to
#             target_rc = root.attrib.get('name', os.path.basename(kcfg_file).replace('.kcfg', 'rc'))
            
#             if target_rc not in mcp_master_schema:
#                 mcp_master_schema[target_rc] = {}

#             for group in root.findall('{http://www.kde.org/standards/kcfg/1.0}group'):
#                 group_name = group.attrib.get('name')
                
#                 if group_name not in mcp_master_schema[target_rc]:
#                     mcp_master_schema[target_rc][group_name] = {}

#                 for entry in group.findall('{http://www.kde.org/standards/kcfg/1.0}entry'):
#                     key_name = entry.attrib.get('name')
#                     key_type = entry.attrib.get('type') # e.g., Int, Bool, Color, Enum
                    
#                     # Extract constraints if they exist
#                     min_val = entry.find('{http://www.kde.org/standards/kcfg/1.0}min')
#                     max_val = entry.find('{http://www.kde.org/standards/kcfg/1.0}max')
#                     label = entry.find('{http://www.kde.org/standards/kcfg/1.0}label')

#                     mcp_master_schema[target_rc][group_name][key_name] = {
#                         "type": key_type,
#                         "min": min_val.text if min_val is not None else None,
#                         "max": max_val.text if max_val is not None else None,
#                         "description": label.text if label is not None else "No description available",
#                         "source_kcfg": os.path.basename(kcfg_file)
#                     }
#         except Exception as e:
#             # Skip files with weird formatting or older versions
#             continue
            
#     return mcp_master_schema

# if __name__ == "__main__":
#     full_schema = parse_all_kcfg()
    
#     with open("mcp_kde_logic.json", "w") as f:
#         json.dump(full_schema, f, indent=4)
    
#     print(f"Generated logic for {len(full_schema)} configuration files.")


# import xml.etree.ElementTree as ET
# import glob
# import json
# import os
# from pathlib import Path

# # Common locations for KDE config definitions on Arch/EndeavourOS
# KCFG_PATHS = [
#     "/usr/share/config.kcfg/*.kcfg",
#     "/usr/share/plasma/shell/contents/config/main.xml", # Panel/Shell logic
#     "/usr/share/kwin/metadata.json" # Modern KWin effects logic
# ]

# def parse_choices(entry, ns):
#     """Extracts valid options for Enum or String types."""
#     choices = []
#     choice_elements = entry.find(f'{ns}choices')
#     if choice_elements is not None:
#         for choice in choice_elements.findall(f'{ns}choice'):
#             name = choice.attrib.get('name')
#             if name:
#                 choices.append(name)
#     return choices if choices else None

# def fix_metadata_miner():
#     mcp_master_schema = {}
#     ns = '{http://www.kde.org/standards/kcfg/1.0}'
    
#     # Expand the search path
#     all_files = []
#     for path in KCFG_PATHS:
#         all_files.extend(glob.glob(path))

#     for kcfg_file in all_files:
#         try:
#             tree = ET.parse(kcfg_file)
#             root = tree.getroot()
            
#             # 1. IDENTIFY TARGET FILE (The --file parameter)
#             # If the file is 'kdeglobals.kcfg', it targets 'kdeglobals'
#             target_rc = root.attrib.get('name')
#             if not target_rc:
#                 target_rc = os.path.basename(kcfg_file).replace('.kcfg', '').replace('.xml', '')
            
#             # Map common internal names to actual filenames
#             mapping = {"kdeglobals": "kdeglobals", "kwinrc": "kwinrc", "plasmarc": "plasmarc"}
#             target_rc = mapping.get(target_rc.lower(), target_rc)

#             if target_rc not in mcp_master_schema:
#                 mcp_master_schema[target_rc] = {}

#             for group in root.findall(f'{ns}group'):
#                 group_name = group.attrib.get('name', 'General')
                
#                 if group_name not in mcp_master_schema[target_rc]:
#                     mcp_master_schema[target_rc][group_name] = {}

#                 for entry in group.findall(f'{ns}entry'):
#                     key_name = entry.attrib.get('name')
#                     key_type = entry.attrib.get('type')
                    
#                     # 2. EXTRACT CHOICES (Solving the "What values to give" problem)
#                     valid_options = parse_choices(entry, ns)
                    
#                     # 3. EXTRACT RELOAD LOGIC
#                     # Some kcfg files have a 'reconfigure' signal or 'emit' tag
#                     # If it's kwinrc, we know it needs a reload.
#                     reload_required = False
#                     if "kwin" in target_rc or "plasma" in target_rc:
#                         reload_required = "qdbus org.kde.KWin /KWin reconfigure"

#                     mcp_master_schema[target_rc][group_name][key_name] = {
#                         "type": key_type,
#                         "options": valid_options,
#                         "min": entry.findtext(f'{ns}min'),
#                         "max": entry.findtext(f'{ns}max'),
#                         "default": entry.findtext(f'{ns}default'),
#                         "description": entry.findtext(f'{ns}label') or "No description",
#                         "reload_cmd": reload_required
#                     }
#         except Exception:
#             continue
            
#     return mcp_master_schema

# if __name__ == "__main__":
#     schema = fix_metadata_miner()
#     with open("mcp_kde_fixed.json", "w") as f:
#         json.dump(schema, f, indent=4)
#     print(f"Fixed schema generated with {len(schema)} files mapped.")



import xml.etree.ElementTree as ET
import glob
import json
import os

def get_clean_schema():
    mcp_schema = {}
    # Expanded search for core ricing components
    paths = [
        "/usr/share/config.kcfg/*.kcfg",
        "/usr/share/plasma/shell/contents/config/main.xml"
    ]
    
    ns = '{http://www.kde.org/standards/kcfg/1.0}'

    for path_pattern in paths:
        for kcfg_file in glob.glob(path_pattern):
            try:
                tree = ET.parse(kcfg_file)
                root = tree.getroot()
                
                # Normalize filename (e.g., kdeglobals, kwinrc)
                target_rc = root.attrib.get('name', os.path.basename(kcfg_file).replace('.kcfg', ''))
                if not target_rc or target_rc == "main": # common for plasma shell
                    target_rc = "plasmarc"
                
                if target_rc not in mcp_schema:
                    mcp_schema[target_rc] = {}

                for group in root.findall(f'{ns}group'):
                    g_name = group.attrib.get('name', 'General')
                    if g_name not in mcp_schema[target_rc]:
                        mcp_schema[target_rc][g_name] = {}

                    for entry in group.findall(f'{ns}entry'):
                        key = entry.attrib.get('name')
                        
                        # FIX 1: Skip nulls and dynamic templates the LLM can't use yet
                        if not key or "$" in key or key == "null":
                            continue

                        # FIX 2: Better type and choice extraction
                        choices = []
                        choice_list = entry.find(f'{ns}choices')
                        if choice_list is not None:
                            choices = [c.attrib.get('name') for c in choice_list.findall(f'{ns}choice') if c.attrib.get('name')]

                        # FIX 3: Logical grouping for the LLM
                        mcp_schema[target_rc][g_name][key] = {
                            "type": entry.attrib.get('type', 'String'),
                            "options": choices if choices else None,
                            "min": entry.findtext(f'{ns}min'),
                            "max": entry.findtext(f'{ns}max'),
                            "description": entry.findtext(f'{ns}label') or f"Control {key} in {g_name}",
                            "command": f"kwriteconfig6 --file {target_rc} --group \"{g_name}\" --key {key}"
                        }
            except:
                continue
    
    # MANUAL INJECTION: Adding the "Holy Grail" ricing keys that are often hidden
    if "kdeglobals" in mcp_schema:
        mcp_schema["kdeglobals"]["KScreen"] = {
            "ScaleFactor": {
                "type": "Double",
                "min": "1.0", "max": "3.0",
                "description": "Global UI Scaling (1.5 = 150%)"
            }
        }
    
    return mcp_schema

if __name__ == "__main__":
    data = get_clean_schema()
    with open("mcp_ricing_schema.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Clean schema generated: mcp_ricing_schema.json")