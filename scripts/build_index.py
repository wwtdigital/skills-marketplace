#!/usr/bin/env python3
"""Build the data the marketplace site reads.

Writes:
  site/data/index.json          catalog of plugins + skills
  site/downloads/<skill>.skill  zip of each skill folder (for people without GitHub)
  site/downloads/<plugin>.zip   zip of each whole plugin

Usage:  python3 scripts/build_index.py [--check]
  --check   build to a temp dir and just report; don't write into site/
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT, iter_skills, load_marketplace, load_plugin_manifest, plugin_dir

SITE = ROOT / "site"
REPO_URL = "https://github.com/wwtdigital/skills-marketplace"


def git(*args) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def last_modified(path: Path) -> str:
    iso = git("log", "-1", "--format=%cI", "--", str(path.relative_to(ROOT)))
    return iso or datetime.now(timezone.utc).isoformat(timespec="seconds")


def zip_dir(src: Path, dest: Path, arc_root: str) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_file() and f.name != ".gitkeep" and "__pycache__" not in f.parts:
                z.write(f, f"{arc_root}/{f.relative_to(src)}")
    return dest.stat().st_size


def first_heading_para(body: str) -> str:
    """First non-heading paragraph of the body, for the card summary."""
    para = []
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("<!--"):
            if para:
                break
            continue
        para.append(s)
    return " ".join(para)[:400]


def build(out: Path) -> dict:
    mp = load_marketplace()
    data_dir, dl_dir = out / "data", out / "downloads"
    data_dir.mkdir(parents=True, exist_ok=True)
    dl_dir.mkdir(parents=True, exist_ok=True)

    index = {
        "marketplace": {
            "name": mp["name"],
            "description": mp.get("description", ""),
            "version": mp.get("version", ""),
            "repo": REPO_URL,
            "install": f"/plugin marketplace add wwtdigital/skills-marketplace",
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "commit": git("rev-parse", "--short", "HEAD"),
        },
        "plugins": [],
    }
    for entry in mp["plugins"]:
        pdir = plugin_dir(entry)
        manifest = load_plugin_manifest(pdir) or {}
        skills = []
        for sk in iter_skills(entry):
            if sk.problems:
                continue
            skill_zip = dl_dir / f"{sk.name}.skill"
            size = zip_dir(sk.path, skill_zip, sk.name)
            skills.append({
                "name": sk.name,
                "description": sk.description,
                "summary": first_heading_para(sk.body),
                "owner": sk.metadata.get("owner", ""),
                "status": sk.metadata.get("status", "draft"),
                "version": str(sk.metadata.get("version", "")),
                "connectors": sk.metadata.get("connectors") or [],
                "has_scripts": (sk.path / "scripts").exists(),
                "has_references": (sk.path / "references").exists(),
                "updated": last_modified(sk.path),
                "source": f"{REPO_URL}/tree/main/{sk.path.relative_to(ROOT)}",
                "download": f"downloads/{sk.name}.skill",
                "download_bytes": size,
            })
        plugin_zip = dl_dir / f"{entry['name']}.zip"
        psize = zip_dir(pdir, plugin_zip, entry["name"])
        index["plugins"].append({
            "name": entry["name"],
            "displayName": entry.get("displayName") or manifest.get("displayName") or entry["name"],
            "description": entry.get("description") or manifest.get("description", ""),
            "category": entry.get("category", ""),
            "tags": entry.get("tags") or manifest.get("keywords") or [],
            "version": entry.get("version") or manifest.get("version", ""),
            "author": (entry.get("author") or manifest.get("author") or {}).get("name", ""),
            "install": f"/plugin install {entry['name']}@{mp['name']}",
            "source": f"{REPO_URL}/tree/main/{pdir.relative_to(ROOT)}",
            "download": f"downloads/{entry['name']}.zip",
            "download_bytes": psize,
            "skills": skills,
        })
    (data_dir / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    return index


def main() -> int:
    check = "--check" in sys.argv
    if check:
        with tempfile.TemporaryDirectory() as td:
            idx = build(Path(td))
    else:
        # clean generated outputs so removed skills disappear
        for sub in ("data", "downloads"):
            shutil.rmtree(SITE / sub, ignore_errors=True)
        idx = build(SITE)
    n_sk = sum(len(p["skills"]) for p in idx["plugins"])
    print(f"{'checked' if check else 'built'} index: {len(idx['plugins'])} plugins, {n_sk} skills"
          + ("" if check else f" → {SITE.relative_to(ROOT)}/data/index.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
