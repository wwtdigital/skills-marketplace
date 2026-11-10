// Run from site/: node --test lib/
import assert from "node:assert/strict";
import { test } from "node:test";
import { headings, slug } from "./markdown.ts";

test("slug lowercases and hyphenates", () => {
  assert.equal(slug("Step 3: Verify (and report)"), "step-3-verify-and-report");
  assert.equal(slug("  "), "");
});

test("headings: h2 and h3 by default, with 1-based lines and plain text", () => {
  const md = ["# Title", "", "intro", "## Workflow", "text", "### Step `one` *now*", "## [Links](x.md) and more"].join("\n");
  assert.deepEqual(headings(md), [
    { id: "workflow", text: "Workflow", level: 2, line: 4 },
    { id: "step-one-now", text: "Step one now", level: 3, line: 6 },
    { id: "links-and-more", text: "Links and more", level: 2, line: 7 },
  ]);
});

test("headings: duplicates get -2, -3", () => {
  const md = "## A\n### Verify\n## B\n### Verify\n### Verify";
  assert.deepEqual(
    headings(md).map((h) => h.id),
    ["a", "verify", "b", "verify-2", "verify-3"],
  );
});

test("headings: lines inside fenced code are skipped", () => {
  const md = ["## Real", "```md", "## Not a heading", "```", "~~~", "### Also not", "~~~", "### Real sub"].join("\n");
  assert.deepEqual(
    headings(md).map((h) => h.text),
    ["Real", "Real sub"],
  );
});

test("headings: level filter for a h2-only contents list", () => {
  assert.deepEqual(
    headings("## A\n### B\n## C", [2]).map((h) => h.id),
    ["a", "c"],
  );
});

test("headings: closing hashes and a heading that slugs to nothing", () => {
  assert.deepEqual(headings("## Done ##\n## ???"), [
    { id: "done", text: "Done", level: 2, line: 1 },
    { id: "section", text: "???", level: 2, line: 2 },
  ]);
});
