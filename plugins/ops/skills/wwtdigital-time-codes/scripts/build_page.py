#!/usr/bin/env python3
"""Build or read the "My Time Codes" page.

  python build_page.py build   <data.json> <out.html>   # data -> page (validated)
  python build_page.py extract <page.html> <data.json>  # page -> data

The template lives at ../references/page-template.html and has exactly one
__DATA__ placeholder inside <script type="application/json" id="bill-codes-data">.
"""
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "references" / "page-template.html"
BLOCK = re.compile(r'<script type="application/json" id="bill-codes-data">\s*(.*?)\s*</script>', re.S)
TYPES = {"project", "sales_pl", "indirect"}
LISTS = ["rows", "standing", "notices", "references", "no_code_channels", "open_questions"]


def fail(msg):
    sys.exit(f"ERROR: {msg}")


def validate(d):
    problems = []
    for key in ["owner", "slack_user_id", "workspace", "generated", "channels_scanned"]:
        if key not in d:
            problems.append(f"missing top-level field '{key}'")
    for key in LISTS:
        d.setdefault(key, [])
        if not isinstance(d[key], list):
            problems.append(f"'{key}' must be a list")
    for i, r in enumerate(d["rows"]):
        for f in ["channel", "channel_id", "code", "code_type"]:
            if not r.get(f):
                problems.append(f"rows[{i}] missing '{f}'")
        if r.get("code_type") not in TYPES:
            problems.append(f"rows[{i}] code_type '{r.get('code_type')}' not in {sorted(TYPES)}")
        r.setdefault("task", "")
        if not r.get("label"):
            r["label"] = "(unlabeled)"
        r.setdefault("found_in", "topic")
    for i, n in enumerate(d["notices"]):
        if not n.get("flag"):
            problems.append(f"notices[{i}] missing 'flag' (short label shown on rows)")
    for i, q in enumerate(d["open_questions"]):
        if q.get("status") not in {"open", "answered"}:
            problems.append(f"open_questions[{i}] status must be 'open' or 'answered'")
    return problems


def build(data_path, out_path):
    d = json.loads(Path(data_path).read_text(encoding="utf-8"))
    problems = validate(d)
    if problems:
        fail("data problems:\n  - " + "\n  - ".join(problems))
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if tpl.count("__DATA__") != 1:
        fail("template must contain exactly one __DATA__ placeholder")
    blob = json.dumps(d, ensure_ascii=False, indent=1).replace("</", "<\\/")
    page = tpl.replace("__DATA__", blob)
    m = BLOCK.search(page)
    if not m:
        fail("data block not found in built page")
    json.loads(m.group(1))  # round-trip check
    Path(out_path).write_text(page, encoding="utf-8")
    chans = {r["channel"] for r in d["rows"]}
    flagged = {c for n in d["notices"] for c in n.get("codes", [])}
    unmatched = sorted(flagged - {r["code"] for r in d["rows"]})
    print(f"OK {out_path}: {len(d['rows'])} code rows across {len(chans)} channels, "
          f"{len(d['standing'])} standing, {len(d['notices'])} notices, "
          f"{sum(q.get('status') == 'open' for q in d['open_questions'])} open questions, "
          f"{d['channels_scanned']} channels scanned")
    if unmatched:
        print(f"NOTE notice codes not in this person's channels: {', '.join(unmatched)}")


def extract(page_path, data_path):
    page = Path(page_path).read_text(encoding="utf-8")
    m = BLOCK.search(page)
    if not m:
        fail("no bill-codes-data block in that page; is it a My Time Codes page?")
    d = json.loads(m.group(1))
    Path(data_path).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK {data_path}: generated {d.get('generated')}, {len(d.get('rows', []))} rows")


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in {"build", "extract"}:
        sys.exit(__doc__)
    (build if sys.argv[1] == "build" else extract)(sys.argv[2], sys.argv[3])
