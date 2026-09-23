#!/usr/bin/env python3
"""Validate marketplace.json, every plugin.json, and every SKILL.md.

Usage:  python3 scripts/validate.py [--strict] [--base REF]
  --strict     treat warnings as errors (CI uses this on main)
  --base REF   also require version bumps for anything changed since REF (CI passes the PR base;
               locally, e.g. --base origin/main). Compares against the working tree, so
               uncommitted changes count.
Exit code 1 on any error.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from common import (DISCIPLINES, KEBAB, ROOT, STATUSES, iter_skills, load_marketplace,
                    load_plugin_manifest, parse_skill_md, plugin_dir)

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
notes: list[str] = []


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
        notes.append(f"plugin '{n}': contains no skills yet")  # expected for new disciplines; not a warning
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


# ---- version bumps -------------------------------------------------------------------------
# plugin.json `version` is what Claude Code compares to decide whether installed users get an
# update, so any shipped change to a plugin without a bump silently never reaches them.

# Changes to these don't alter what Claude loads, so they don't need a bump.
NO_BUMP_NEEDED = {"README.md", ".gitkeep"}


def git(*args: str) -> str | None:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def semver(v) -> tuple[int, ...] | None:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(v or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def bumped(old, new) -> bool:
    o, n = semver(old), semver(new)
    return n > o if (o and n) else str(new) != str(old)


def check_version_bumps(mp: dict, base: str) -> None:
    mb = (git("merge-base", base, "HEAD") or "").strip()
    if not mb:
        err(f"--base {base}: not a git ref this checkout knows (fetch it, or use fetch-depth: 0 in CI)")
        return
    changed = set((git("diff", "--name-only", mb) or "").split())
    changed |= set((git("ls-files", "--others", "--exclude-standard") or "").split())

    def at_base(rel: str) -> str | None:
        return git("show", f"{mb}:{rel}")

    base_mp = at_base(".claude-plugin/marketplace.json")
    if base_mp:
        old = json.loads(base_mp)
        if {p["name"] for p in old.get("plugins", [])} != {p["name"] for p in mp.get("plugins", [])} \
                and not bumped(old.get("version"), mp.get("version")):
            err(f"marketplace.json: plugins were added, removed or renamed but version is still "
                f"{mp.get('version')} (bump it)")

    for entry in mp.get("plugins", []):
        pdir = plugin_dir(entry)
        prel = pdir.relative_to(ROOT).as_posix()
        shipped = sorted(f for f in changed
                         if f.startswith(prel + "/") and Path(f).name not in NO_BUMP_NEEDED)
        if not shipped:
            continue
        manifest_rel = f"{prel}/.claude-plugin/plugin.json"
        old_manifest = at_base(manifest_rel)
        if old_manifest is None:
            continue  # new plugin: nothing installed to update
        old_v = json.loads(old_manifest).get("version")
        new_v = (load_plugin_manifest(pdir) or {}).get("version")
        if not bumped(old_v, new_v):
            err(f"plugin '{entry['name']}': {len(shipped)} file(s) changed since {base} "
                f"(e.g. {shipped[0]}) but plugin.json version {new_v} isn't above {old_v} — "
                f"installed users won't get the change until it's bumped")
        for sk in iter_skills(entry):
            srel = sk.path.relative_to(ROOT).as_posix()
            if not any(f.startswith(srel + "/") for f in shipped) or sk.problems:
                continue
            old_md = at_base(f"{srel}/SKILL.md")
            if old_md is None:
                continue  # new skill
            try:
                old_sv = (parse_skill_md(old_md)[0].get("metadata") or {}).get("version")
            except ValueError:
                continue
            if not bumped(old_sv, sk.metadata.get("version")):
                err(f"{entry['name']}/{sk.name}: changed since {base} but metadata.version "
                    f"{sk.metadata.get('version')} isn't above {old_sv}")


def main() -> int:
    strict = "--strict" in sys.argv
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv[:-1] else None
    mp = load_marketplace()
    check_marketplace(mp)
    for entry in mp.get("plugins", []):
        check_plugin(entry)
    # skill names must be unique marketplace-wide: downloads and site routes are keyed by name alone
    seen: dict[str, str] = {}
    for entry in mp.get("plugins", []):
        if "source" not in entry or not plugin_dir(entry).is_dir():
            continue
        for sk in iter_skills(entry):
            if sk.name in seen:
                err(f"{entry['name']}/{sk.name}: skill name already used in plugin '{seen[sk.name]}'")
            seen.setdefault(sk.name, entry["name"])
    if base:
        check_version_bumps(mp, base)
    for n in notes:
        print(f"NOTE  {n}")
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
