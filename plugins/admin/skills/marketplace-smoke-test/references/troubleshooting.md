# Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Skill never triggers | Plugin not installed or disabled | `/plugin` → check `admin@wwtdigital` is enabled |
| Skill version lower than the site shows | Cached install | `/plugin marketplace update wwtdigital`, then reinstall the plugin |
| Install type is `standalone` but you installed the plugin | A downloaded `.skill` copy in `~/.claude/skills/` is shadowing it | Remove the standalone copy |
| Install type is `plugin` but the manifest `name` isn't `admin` | The skill folder was copied into another plugin, or loaded from a checkout of a different repo | Show the path; reinstall from the marketplace if it isn't `admin` |
| `plugin.json` exists but can't be read | Partial or corrupted install | `/plugin uninstall admin@wwtdigital`, then `/plugin install admin@wwtdigital` |
| Claude can't tell which folder the skill was loaded from | The client doesn't expose the base directory | Report the skill version from the frontmatter and mark install type as unknown |
