#!/usr/bin/env python3
import os
import json
from functools import reduce
from typing import List, Dict, Any, Tuple

def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''

def list_files(base: str) -> List[str]:
    return [os.path.join(base, f) for f in os.listdir(base) if os.path.isfile(os.path.join(base, f))]

def list_dirs(base: str) -> List[str]:
    return [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]

def summarize_yaml(filename: str, content: str) -> str:
    return f"### `{filename}`\n\n```yaml\n{content[:2000]}{'\n...\n' if len(content) > 2000 else ''}```\n"

def summarize_dir(dirname: str) -> str:
    files = list_files(dirname)
    return f"### `{os.path.basename(dirname)}/`\n\nContains {len(files)} files.\n\n" + '\n'.join([f"- `{os.path.basename(f)}`" for f in files]) + '\n'

def summarize_entities(json_path: str) -> str:
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            entities = json.load(f)
    except Exception:
        return "Could not load entities.json."
    def entity_md(e: Dict[str, Any]) -> str:
        attrs = e.get('attributes', {})
        attrs_md = '\n'.join([f"    - `{k}`: `{v}`" for k, v in attrs.items()])
        return f"- **{e.get('entity_id', 'unknown')}**\n  - state: `{e.get('state', '')}`\n  - attributes:\n{attrs_md if attrs_md else '    - (none)'}"
    return "## Home Assistant Entities (from /api/states)\n\n" + '\n\n'.join(map(entity_md, entities))

def summarize_devices(json_path: str) -> str:
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            devices = json.load(f)
    except Exception:
        return "Could not load devices.json."
    if not devices:
        return "No devices found."
    def device_md(d: Dict[str, Any]) -> str:
        return f"- **ID:** `{d.get('id', '')}` | **Name:** `{d.get('name', '')}` | **Model:** `{d.get('model', '')}` | **Manufacturer:** `{d.get('manufacturer', '')}`"
    return "## Home Assistant Devices (from SQLite DB)\n\n" + '\n'.join(map(device_md, devices))

def summarize_registry(device_registry_path: str, entity_registry_path: str) -> str:
    try:
        with open(device_registry_path, 'r', encoding='utf-8') as f:
            device_data = json.load(f)
        with open(entity_registry_path, 'r', encoding='utf-8') as f:
            entity_data = json.load(f)
    except Exception as e:
        return f"## Home Assistant Device & Entity Registry (core.device_registry / core.entity_registry)\n\nCould not load or parse registry files: {e}"
    devices = {d['id']: d for d in device_data.get('data', {}).get('devices', [])}
    entities = entity_data.get('data', {}).get('entities', [])
    # Map device_id to entities
    device_entities = {}
    for e in entities:
        dev_id = e.get('device_id')
        if dev_id:
            device_entities.setdefault(dev_id, []).append(e)
    lines = ["## Home Assistant Device & Entity Registry (core.device_registry / core.entity_registry)\n"]
    for dev_id, dev in devices.items():
        lines.append(f"- **Device ID:** `{dev_id}` | **Name:** `{dev.get('name_by_user') or dev.get('name', '')}` | **Model:** `{dev.get('model', '')}` | **Manufacturer:** `{dev.get('manufacturer', '')}`")
        ents = device_entities.get(dev_id, [])
        if ents:
            lines.append("    - Entities:")
            for ent in ents:
                lines.append(f"        - `{ent.get('entity_id')}` (Platform: {ent.get('platform', '')}, Original Name: {ent.get('original_name', '')})")
    if not devices:
        lines.append("No devices found in registry.")
    return '\n'.join(lines)

def main():
    # Try to change to the directory containing core.device_registry if it exists
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, 'core.device_registry')):
        pass  # already in the right directory
    else:
        # Try to use AI_BASE_DIR env var if set
        ai_dir = os.environ.get('AI_BASE_DIR')
        if ai_dir and os.path.exists(os.path.join(ai_dir, 'core.device_registry')):
            os.chdir(ai_dir)
            cwd = ai_dir
    files = list_files(cwd)
    dirs = list_dirs(cwd)
    md_sections = []
    # YAML and DB files
    for fname in files:
        if fname.endswith('.yaml'):
            md_sections.append(summarize_yaml(os.path.basename(fname), read_file(fname)))
    # Directories
    for dname in dirs:
        if os.path.basename(dname) in ['custom_components', 'blueprints']:
            md_sections.append(summarize_dir(dname))
    # Registries
    device_registry = os.path.join(cwd, 'core.device_registry')
    entity_registry = os.path.join(cwd, 'core.entity_registry')
    md_sections.append(summarize_registry(device_registry, entity_registry))
    # Entities
    entities_json = os.path.join(cwd, 'entities.json')
    if os.path.exists(entities_json):
        md_sections.append(summarize_entities(entities_json))
    # Devices
    devices_json = os.path.join(cwd, 'devices.json')
    if os.path.exists(devices_json):
        md_sections.append(summarize_devices(devices_json))
    # Write output
    with open(os.path.join(cwd, 'home_assistant_full_export.md'), 'w', encoding='utf-8') as f:
        f.write("# Home Assistant Full Export for AI\n\n")
        f.write("\n---\n\n".join(md_sections))

if __name__ == '__main__':
    main() 