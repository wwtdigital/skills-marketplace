#!/usr/bin/env python3
"""Validate marketplace.json, every plugin.json, and every SKILL.md.

Usage:  python3 scripts/validate.py [--strict]
  --strict   treat warnings as errors (CI uses this on main)
Exit code 1 on any error.
"""
from __future__ import annotations

import re
import sys

from common import (DISCIPLINES, KEBAB, ROOT, STATUSES, iter_skills, load_marketplace,
                    load_plugin_manifest, plugin_dir)

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),        # Slack
    re.compile(r"ghp_[A-Za-z0-9]{36}"),                  # GitHub PAT
    re.compile(r"glpat-[A-Za-z0-9\-]{20,}"),             # GitLab PAT
    re.compile(r"AKIA[0-9A-Z]{16}"),                     # AWS
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

errors: list[str] = []
warnings: list[str] = []


def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)


def check_marketplace(mp: dict) -> None:
    for k in ("name", "owner", "plugins"):
        if k not in mp:
            err(f"marketplace.json: missing required field '{k}'")
    if "owner" in mp and "name" not in mp["owner"]:
        err("marketplace.json: owner.name is required")
    if not KEBAB.match(mp.get("name", "")):
        err(f"marketplace.json: name '{mp.get('name')}' must be kebab-case")
    names = [p.get("name") for p in mp.get("plugins", [])]
    dups = {n for n in names if names.count(n) > 1}
    if dups:
        err(f"marketplace.json: duplicate plugin names {sorted(dups)}")
    for ren_from, ren_to in (mp.get("renames") or {}).items():
        if ren_to is not None and ren_to not in names:
            err(f"marketplace.json: renames['{ren_from}'] -> '{ren_to}' is not a listed plugin")


def check_plugin(entry: dict) -> None:
    n = entry.get("name", "?")
    if not KEBAB.match(n):
        err(f"plugin '{n}': name must be kebab-case")
    if "source" not in entry:
        err(f"plugin '{n}': missing 'source'")
        return
    pdir = plugin_dir(entry)
    if not pdir.is_dir():
        err(f"plugin '{n}': source directory {pdir.relative_to(ROOT)} does not exist")
        return
    if ".." in str(entry["source"]):
        err(f"plugin '{n}': source must not escape the marketplace root")
    manifest = load_plugin_manifest(pdir)
    if manifest is None:
        err(f"plugin '{n}': missing .claude-plugin/plugin.json")
    else:
        if manifest.get("name") != n:
            err(f"plugin '{n}': plugin.json name '{manifest.get('name')}' does not match marketplace entry")
        if "version" not in manifest:
            warn(f"plugin '{n}': plugin.json has no version (users won't get pinned updates)")
    if not (pdir / "README.md").exists():
        warn(f"plugin '{n}': no README.md")
    if not entry.get("description"):
        warn(f"plugin '{n}': no description in marketplace entry")

    skills = iter_skills(entry)
    if not skills:
        warn(f"plugin '{n}': contains no skills yet")
    for sk in skills:
        for p in sk.problems:
            err(f"{n}/{sk.name}: {p}")
        if sk.problems and not sk.description:
            continue
        check_skill(n, sk)


def check_skill(plugin: str, sk) -> None:
    tag = f"{plugin}/{sk.name}"
    if not KEBAB.match(sk.name):
        err(f"{tag}: skill folder must be kebab-case")
    d = sk.description
    if not d:
        err(f"{tag}: description is required")
    else:
        if len(d) > 1024:
            err(f"{tag}: description is {len(d)} chars (max 1024)")
        if len(d) < 80:
            warn(f"{tag}: description is short ({len(d)} chars) — say when to use it, with trigger phrases")
        if not re.search(r"(?i)\buse (this |it )?when\b|\btrigger", d):
            warn(f"{tag}: description doesn't say when to use it ('Use when …')")
    md = sk.metadata
    if not md:
        warn(f"{tag}: no metadata block (owner, discipline, status)")
    else:
        owner = str(md.get("owner", ""))
        if not owner.endswith("@wwt.com"):
            err(f"{tag}: metadata.owner must be a @wwt.com address (got '{owner}')")
        if md.get("discipline") not in DISCIPLINES:
            err(f"{tag}: metadata.discipline must be one of {sorted(DISCIPLINES)}")
        if md.get("status") not in STATUSES:
            err(f"{tag}: metadata.status must be one of {sorted(STATUSES)}")
        if "version" not in md:
            warn(f"{tag}: metadata.version missing")
    lines = sk.body.count("\n")
    if lines > 250:
        warn(f"{tag}: SKILL.md body is {lines} lines — move detail into references/")
    if "verif" not in sk.body.lower() and "check" not in sk.body.lower():
        warn(f"{tag}: no verification step mentioned in the workflow")
    # secrets scan across the whole skill folder
    for f in sk.path.rglob("*"):
        if f.is_file() and f.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".pptx", ".docx", ".xlsx", ".zip"}:
            try:
                txt = f.read_text(errors="ignore")
            except Exception:
                continue
            for pat in SECRET_PATTERNS:
                if pat.search(txt):
                    err(f"{tag}: possible secret in {f.relative_to(ROOT)} (pattern {pat.pattern[:30]}…)")
                    break


def main() -> int:
    strict = "--strict" in sys.argv
    mp = load_marketplace()
    check_marketplace(mp)
    for entry in mp.get("plugins", []):
        check_plugin(entry)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    n_plugins = len(mp.get("plugins", []))
    n_skills = sum(len(iter_skills(e)) for e in mp.get("plugins", []) if "source" in e)
    print(f"\n{n_plugins} plugins, {n_skills} skills — {len(errors)} errors, {len(warnings)} warnings")
    if errors or (strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
