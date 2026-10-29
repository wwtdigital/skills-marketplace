// Pure helpers only: split a skill's frontmatter description into the parts a TL;DR shows.
// Descriptions follow CONTRIBUTING's "what + when (with trigger phrases) + not-for" pattern, so
// the cues are "Use when…" (or "Use whenever…", "Use this when…", "Trigger when…") and "Not for…".
// Nothing here is required to be present: a description that doesn't follow the pattern comes back
// as `what` alone, and the page falls back to showing it whole.

export type SkillSummary = {
  /** The first sentence of the "what" part: one plain line of what the skill does. */
  lead: string;
  /** The rest of the "what" part after the lead, if any. */
  more: string;
  /** The trigger prose, from the "Use when" cue up to (not including) "Not for". */
  when: string;
  /** Quoted phrases inside `when`: what to say to make Claude load the skill. */
  sayThis: string[];
  /** The "Not for" part, with the words "Not for" left on so it reads as a sentence. */
  notFor: string;
};

// A cue only counts at the start of a sentence (or of the text), so "a tool to use for X" inside the
// what-part doesn't split it. "Also use…" is deliberately not a cue: it extends a trigger sentence.
const WHEN_CUE = /(?:^|[.;:!?]\s+|\(\s*)(Use (?:this |it )?(?:when|whenever|if|to|for|before|after|any ?time|every ?time)\b|Trigger (?:this |it )?(?:when|whenever|if|on)\b)/i;
const NOT_FOR_CUE = /(?:^|[.;!?]\s+|\(\s*)(Not for\b|Never for\b|(?:Don't|Do not|Never) use (?:this |it )?(?:for|when|to|on)\b)/i;

// Straight or curly double quotes, 2..160 chars, no quote inside. Trailing punctuation the writer
// tucked inside the quotes ("look at the pursuit channel,") is not part of the phrase.
const QUOTED = /["“]([^"“”]{2,160})["”]/g;

const collapse = (s: string) => s.replace(/\s+/g, " ").trim();

/** Index where a cue's captured phrase starts, or -1. */
function cueIndex(text: string, cue: RegExp, from = 0): number {
  const m = cue.exec(text.slice(from));
  return m ? from + m.index + m[0].length - m[1].length : -1;
}

/** Split prose into sentences on ". " / "! " / "? " followed by a capital, quote or bracket. */
export function sentences(text: string): string[] {
  return collapse(text)
    .split(/(?<=[.!?])\s+(?=["“(\[A-Z])/)
    .map((s) => s.trim())
    .filter(Boolean);
}

/** The quoted phrases in a piece of text, in order, trimmed and deduplicated case-insensitively. */
export function quotedPhrases(text: string): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const m of text.matchAll(QUOTED)) {
    const phrase = m[1].replace(/^[\s,.;:]+|[\s,.;:]+$/g, ""); // a trailing ? or ! is part of what you would say
    const key = phrase.toLowerCase();
    if (phrase && !seen.has(key)) {
      seen.add(key);
      out.push(phrase);
    }
  }
  return out;
}

export function summarizeDescription(description: string): SkillSummary {
  const text = collapse(description);
  const whenAt = cueIndex(text, WHEN_CUE);
  // "Not for" is looked for after the trigger cue when there is one, so a what-part that happens to
  // say "not for" mid-sentence can't swallow the triggers.
  const notForAt = cueIndex(text, NOT_FOR_CUE, Math.max(whenAt, 0));

  const whatEnd = whenAt >= 0 ? whenAt : notForAt >= 0 ? notForAt : text.length;
  const whenEnd = notForAt >= 0 ? notForAt : text.length;
  const what = text.slice(0, whatEnd).trim();
  const when = whenAt >= 0 ? text.slice(whenAt, whenEnd).trim() : "";
  const notFor = notForAt >= 0 ? text.slice(notForAt).trim() : "";

  const [lead = "", ...rest] = sentences(what);
  return { lead, more: rest.join(" "), when, sayThis: quotedPhrases(when), notFor };
}
