// Run from site/: node --test lib/
import assert from "node:assert/strict";
import { test } from "node:test";
import { quotedPhrases, sentences, summarizeDescription } from "./skill-summary.ts";

const HUMANIZER = `Remove AI writing patterns from text: hard bans (em dashes, Claude-isms,
  negative parallelism, bold-first bullets) and voice problems (corporate jargon),
  through a tiered audit. Use when someone asks for it directly: "humanize this",
  "make it sound less like AI", "de-AI this", "does this read as AI?", or when someone
  asks for a final pass on text before it goes to a real person. Not for
  flagging AI writing in a document without changing it (a separate skill),
  for brand or visual style, or for writing new content from scratch.`;

test("splits a what / use when / not for description", () => {
  const s = summarizeDescription(HUMANIZER);
  assert.equal(
    s.lead,
    "Remove AI writing patterns from text: hard bans (em dashes, Claude-isms, negative parallelism, bold-first bullets) and voice problems (corporate jargon), through a tiered audit.",
  );
  assert.equal(s.more, "");
  assert.ok(s.when.startsWith("Use when someone asks for it directly"));
  assert.ok(s.when.endsWith("before it goes to a real person."));
  assert.deepEqual(s.sayThis, ["humanize this", "make it sound less like AI", "de-AI this", "does this read as AI?"]);
  assert.ok(s.notFor.startsWith("Not for flagging AI writing"));
  assert.ok(s.notFor.endsWith("from scratch."));
});

test("several what-sentences: the first is the lead, the rest is 'more'", () => {
  const s = summarizeDescription(
    `Build a brief for a pursuit at any stage: RFP, RFI, or nothing yet. Reads the channel and the deck. ` +
      `Produces a published brief. Use whenever someone asks to "look at the pursuit channel," "size this proposal," ` +
      `or asks for Q&A prep. Trigger even if they only name the client. Not for writing the proposal itself, the SOW, or the estimate.`,
  );
  assert.equal(s.lead, "Build a brief for a pursuit at any stage: RFP, RFI, or nothing yet.");
  assert.equal(s.more, "Reads the channel and the deck. Produces a published brief.");
  assert.ok(s.when.includes("Trigger even if they only name the client."));
  assert.deepEqual(s.sayThis, ["look at the pursuit channel", "size this proposal"]);
  assert.equal(s.notFor, "Not for writing the proposal itself, the SOW, or the estimate.");
});

test("quotes in the what-part (email subjects) are not trigger phrases", () => {
  const s = summarizeDescription(
    `Turn MyTime emails ("Action Required: Complete Your Review") into Slack nudges. Use when a manager says ` +
      `"nudge my team", or asks what to do. Needs Slack. Not for approving timecards.`,
  );
  assert.deepEqual(s.sayThis, ["nudge my team"]);
  assert.equal(s.when, 'Use when a manager says "nudge my team", or asks what to do. Needs Slack.');
});

test("'Use this whenever' and curly quotes count", () => {
  const s = summarizeDescription(
    "Answer onboarding questions from Notion. Use this whenever someone asks “how do I get my laptop” or “when's my first paycheck” (even without saying “onboarding”). Also use to audit articles.",
  );
  assert.equal(s.lead, "Answer onboarding questions from Notion.");
  assert.deepEqual(s.sayThis, ["how do I get my laptop", "when's my first paycheck", "onboarding"]);
  assert.ok(s.when.endsWith("Also use to audit articles."));
  assert.equal(s.notFor, "");
});

test("'use' mid-sentence in the what-part does not split it", () => {
  const s = summarizeDescription("A checklist people use for reviews, with the steps to use when they differ. Use when asked to review a wave. Not for new plans.");
  assert.equal(s.lead, "A checklist people use for reviews, with the steps to use when they differ.");
  assert.equal(s.when, "Use when asked to review a wave.");
});

test("no trigger phrases: 'when' is prose and sayThis is empty", () => {
  const s = summarizeDescription("Plan a project. Use when the user wants to plan a project or break an epic into stories. Not for reviewing a wave (use wave-review).");
  assert.deepEqual(s.sayThis, []);
  assert.equal(s.when, "Use when the user wants to plan a project or break an epic into stories.");
  assert.equal(s.notFor, "Not for reviewing a wave (use wave-review).");
});

test("a description with none of the cues comes back as the lead alone", () => {
  const s = summarizeDescription("Does one thing well. Does it fast.");
  assert.equal(s.lead, "Does one thing well.");
  assert.equal(s.more, "Does it fast.");
  assert.equal(s.when, "");
  assert.deepEqual(s.sayThis, []);
  assert.equal(s.notFor, "");
});

test("empty input", () => {
  assert.deepEqual(summarizeDescription(""), { lead: "", more: "", when: "", sayThis: [], notFor: "" });
});

test("quotedPhrases trims tucked-in punctuation and dedupes", () => {
  assert.deepEqual(quotedPhrases('say "a thing," then "A thing" or "b."'), ["a thing", "b"]);
});

test("sentences keeps abbreviations and inline domains together", () => {
  assert.deepEqual(sentences("Checks claims against wwt.com and the record. Then stops."), [
    "Checks claims against wwt.com and the record.",
    "Then stops.",
  ]);
});
