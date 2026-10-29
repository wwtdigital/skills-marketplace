// Pure helpers for the markdown we render: heading ids and tables of contents. Prose.tsx gives
// each heading the id computed here, so a TOC built from the source text and the rendered page
// always agree, and deep links (#heading) are stable as long as the heading text is.

export type Heading = { id: string; text: string; level: number; line: number };

export const slug = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

/** Heading text as it reads: inline code/emphasis markers and link targets removed. */
const plain = (raw: string) =>
  raw
    .replace(/\s+#+\s*$/, "") // closing ### on ATX headings
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1") // [text](url) -> text
    .replace(/[`*_~]/g, "")
    .trim();

/**
 * The `##`/`###` headings of a markdown doc (fenced code blocks skipped), each with the id Prose gives
 * it. Duplicate texts get -2, -3… so every id on a page is unique. `line` is 1-based, matching the
 * position react-markdown reports for the node.
 */
export function headings(md: string, levels: number[] = [2, 3]): Heading[] {
  const out: Heading[] = [];
  const seen = new Map<string, number>();
  let fence: string | null = null;
  md.split(/\r?\n/).forEach((line, i) => {
    const f = /^\s{0,3}(`{3,}|~{3,})/.exec(line);
    if (f) {
      if (!fence) fence = f[1][0];
      else if (f[1][0] === fence) fence = null;
      return;
    }
    if (fence) return;
    const m = /^\s{0,3}(#{1,6})\s+(.+?)\s*$/.exec(line);
    if (!m || !levels.includes(m[1].length)) return;
    const text = plain(m[2]);
    const base = slug(text) || "section";
    const n = (seen.get(base) ?? 0) + 1;
    seen.set(base, n);
    out.push({ id: n === 1 ? base : `${base}-${n}`, text, level: m[1].length, line: i + 1 });
  });
  return out;
}
