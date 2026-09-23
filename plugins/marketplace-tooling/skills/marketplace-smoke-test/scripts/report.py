#!/usr/bin/env python3
"""Print what this installed copy of the skill can see about itself. Stdlib only, read-only."""
import json
import re
from pathlib import Path

skill_dir = Path(__file__).resolve().parent.parent
fm = (skill_dir / "SKILL.md").read_text()
m = re.search(r"^\s*version:\s*['\"]?([^'\"\s]+)", fm, re.M)

# Installed as a plugin: <plugin>/skills/<skill>/ with <plugin>/.claude-plugin/plugin.json
manifest = skill_dir.parent.parent / ".claude-plugin" / "plugin.json"
plugin = json.loads(manifest.read_text()) if manifest.exists() else None

print(json.dumps({
    "skill": skill_dir.name,
    "skill_version": m.group(1) if m else None,
    "install_type": "plugin" if plugin else "standalone",
    "plugin": plugin.get("name") if plugin else None,
    "plugin_version": plugin.get("version") if plugin else None,
    "path": str(skill_dir),
}, indent=2))
