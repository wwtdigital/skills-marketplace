#!/usr/bin/env python3
"""
PostToolUse hook: after a Write or Edit to an HTML file that contains slides, run the static
lint on it. Reads the hook payload on stdin. Standard library only, and never fails the tool
call: a lint problem is reported, not enforced here.

Replaces a shell one-liner that needed jq, which most machines do not have, so the hook was
silently doing nothing for them.
"""
import json, os, re, subprocess, sys

try:
    path = (json.load(sys.stdin).get("tool_input") or {}).get("file_path") or ""
except Exception:
    sys.exit(0)
if not path.lower().endswith(".html") or not os.path.isfile(path):
    sys.exit(0)
try:
    with open(path, encoding="utf-8", errors="replace") as fh:
        if not re.search(r'class="[^"]*slide', fh.read()):
            sys.exit(0)
except OSError:
    sys.exit(0)
lint = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint_source.py")
subprocess.run([sys.executable, lint, path, "--quiet"])
sys.exit(0)
