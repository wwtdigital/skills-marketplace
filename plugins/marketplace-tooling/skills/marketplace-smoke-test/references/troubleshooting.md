# Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Skill never triggers | Plugin not installed or disabled | `/plugin` → check `marketplace-tooling@wwt-digital` is enabled |
| `skill_version` older than the site shows | Cached install | `/plugin marketplace update wwt-digital`, then reinstall the plugin |
| `install_type` is `standalone` but you installed the plugin | A downloaded `.skill` copy in `~/.claude/skills/` is shadowing it | Remove the standalone copy |
| Script fails with `python3: not found` | No Python on PATH | Install Python 3, or skip the script check |
