"""Shared helpers for marketplace scripts. Stdlib + PyYAML only."""
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE_JSON = ROOT / ".claude-plugin" / "marketplace.json"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DISCIPLINES = {"creative-tech", "engineering", "brand-and-voice", "delivery", "data-ai", "tooling"}
STATUSES = {"draft", "beta", "stable"}
# Changes to these don't alter what Claude loads, so they don't count as a change needing a bump.
NO_BUMP_NEEDED = {"README.md", ".gitkeep", ".DS_Store"}


@dataclass
class Skill:
    plugin: str
    name: str
    path: Path
    description: str
    metadata: dict
    body: str
    problems: list[str] = field(default_factory=list)


def load_marketplace() -> dict:
    return json.loads(MARKETPLACE_JSON.read_text())


def content_hash(root: Path) -> str:
    """Stable hash of everything under root that ships to users (paths + bytes)."""
    h = hashlib.sha256()
    for f in sorted(p for p in root.rglob("*") if p.is_file()):
        if f.name in NO_BUMP_NEEDED or "__pycache__" in f.parts:
            continue
        h.update(f.relative_to(root).as_posix().encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def load_prev_catalog(src: str | None, mp: dict) -> dict | None:
    """The previously published site catalog, used as the baseline for version-bump checks and
    'updated' dates. src is a path, a URL, or 'auto' (metadata.site + /data/index.json).
    Returns None if there isn't one yet (first deploy) or it can't be fetched."""
    if not src:
        return None
    if src == "auto":
        site = (mp.get("metadata") or {}).get("site")
        if not site:
            return None
        src = site.rstrip("/") + "/data/index.json"
    try:
        if src.startswith(("http://", "https://")):
            with urllib.request.urlopen(src, timeout=15) as r:
                return json.load(r)
        return json.loads(Path(src).read_text())
    except Exception as e:  # noqa: BLE001 — any failure means "no baseline"
        print(f"NOTE  no previous catalog at {src} ({e.__class__.__name__}); skipping baseline checks")
        return None


def plugin_dir(entry: dict) -> Path:
    src = entry["source"]
    if not isinstance(src, str):
        raise ValueError(f"{entry['name']}: only relative-path sources are supported by these scripts")
    if src.startswith("./"):
        return ROOT / src[2:]
    return ROOT / "plugins" / src  # bare name under metadata.pluginRoot


def load_plugin_manifest(pdir: Path) -> dict | None:
    f = pdir / ".claude-plugin" / "plugin.json"
    return json.loads(f.read_text()) if f.exists() else None


def parse_skill_md(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Raises ValueError if no frontmatter."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("missing YAML frontmatter (--- ... ---)")
    fm = yaml.safe_load(m.group(1)) or {}
    if not isinstance(fm, dict):
        raise ValueError("frontmatter must be a mapping")
    return fm, m.group(2)


def iter_skills(entry: dict) -> list[Skill]:
    pdir = plugin_dir(entry)
    skills: list[Skill] = []
    sdir = pdir / "skills"
    if not sdir.exists():
        return skills
    for d in sorted(p for p in sdir.iterdir() if p.is_dir()):
        f = d / "SKILL.md"
        sk = Skill(plugin=entry["name"], name=d.name, path=d, description="", metadata={}, body="")
        if not f.exists():
            sk.problems.append("folder has no SKILL.md")
            skills.append(sk)
            continue
        try:
            fm, body = parse_skill_md(f.read_text())
        except ValueError as e:
            sk.problems.append(str(e))
            skills.append(sk)
            continue
        sk.description = str(fm.get("description", "")).strip()
        sk.metadata = fm.get("metadata") or {}
        sk.body = body
        if fm.get("name") != d.name:
            sk.problems.append(f"frontmatter name '{fm.get('name')}' != folder name '{d.name}'")
        skills.append(sk)
    return skills
