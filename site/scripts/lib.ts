// Shared loaders for the catalog scripts (validate.ts, build-index.ts). They operate on the
// whole repo, not just site/: marketplace.json is the source of truth for which plugins exist.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { parse as parseYaml } from "yaml";
import type { Catalog } from "../lib/catalog.ts";

export const ROOT = path.resolve(import.meta.dirname, "../..");
export const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;
// One plugin per category; a skill's metadata.category must name the plugin it lives in.
export const CATEGORIES = ["presentation", "research", "ops", "admin", "tech"];
export const STATUSES = ["beta", "draft", "stable"];
// Changes to these don't alter what Claude loads, so they don't count as a change needing a bump.
export const NO_BUMP_NEEDED = new Set(["README.md", ".gitkeep", ".DS_Store"]);

export type MarketplaceEntry = { name: string; source?: unknown; [k: string]: unknown };
export type Marketplace = {
  name: string;
  version?: string;
  owner?: { name?: string };
  metadata?: { site?: string; pluginRoot?: string };
  plugins: MarketplaceEntry[];
  renames?: Record<string, string | null>;
  [k: string]: unknown;
};
export type PluginManifest = { name?: string; version?: string; [k: string]: unknown };
export type SkillMetadata = {
  owner?: string;
  category?: string;
  status?: string;
  connectors?: string[];
  version?: string | number;
  [k: string]: unknown;
};
export type SkillSource = {
  plugin: string;
  name: string;
  dir: string;
  description: string;
  metadata: SkillMetadata;
  body: string;
  problems: string[];
};

export const rel = (p: string) => path.relative(ROOT, p).split(path.sep).join("/");

export function loadMarketplace(): Marketplace {
  return JSON.parse(readFileSync(path.join(ROOT, ".claude-plugin", "marketplace.json"), "utf8"));
}

export function pluginDir(entry: MarketplaceEntry): string {
  const src = entry.source;
  if (typeof src !== "string") throw new Error(`${entry.name}: only relative-path sources are supported by these scripts`);
  return src.startsWith("./") ? path.join(ROOT, src.slice(2)) : path.join(ROOT, "plugins", src); // bare name under pluginRoot
}

export function loadPluginManifest(pdir: string): PluginManifest | null {
  const f = path.join(pdir, ".claude-plugin", "plugin.json");
  return existsSync(f) ? JSON.parse(readFileSync(f, "utf8")) : null;
}

/** Returns [frontmatter, body]. Throws if there's no frontmatter. */
export function parseSkillMd(text: string): [Record<string, unknown>, string] {
  const m = /^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/.exec(text);
  if (!m) throw new Error("missing YAML frontmatter (--- ... ---)");
  const fm = parseYaml(m[1]) ?? {};
  if (typeof fm !== "object" || Array.isArray(fm)) throw new Error("frontmatter must be a mapping");
  return [fm as Record<string, unknown>, m[2]];
}

const isDir = (p: string) => existsSync(p) && statSync(p).isDirectory();

export function iterSkills(entry: MarketplaceEntry): SkillSource[] {
  const sdir = path.join(pluginDir(entry), "skills");
  if (!isDir(sdir)) return [];
  return readdirSync(sdir)
    .filter((d) => isDir(path.join(sdir, d)))
    .sort()
    .map((name) => {
      const dir = path.join(sdir, name);
      const sk: SkillSource = { plugin: entry.name, name, dir, description: "", metadata: {}, body: "", problems: [] };
      const f = path.join(dir, "SKILL.md");
      if (!existsSync(f)) {
        sk.problems.push("folder has no SKILL.md");
        return sk;
      }
      try {
        const [fm, body] = parseSkillMd(readFileSync(f, "utf8"));
        sk.description = String(fm.description ?? "").trim();
        sk.metadata = (fm.metadata as SkillMetadata) || {};
        sk.body = body;
        if (fm.name !== name) sk.problems.push(`frontmatter name '${fm.name}' != folder name '${name}'`);
      } catch (e) {
        sk.problems.push((e as Error).message);
      }
      return sk;
    });
}

/** Every file under dir, sorted by path segments (so a/b sorts before a-b/c). */
export function walk(dir: string): string[] {
  const out: string[] = [];
  const visit = (d: string) => {
    for (const name of readdirSync(d)) {
      const p = path.join(d, name);
      if (statSync(p).isDirectory()) visit(p);
      else out.push(p);
    }
  };
  if (isDir(dir)) visit(dir);
  const key = (p: string) => path.relative(dir, p).split(path.sep);
  return out.sort((a, b) => {
    const [x, y] = [key(a), key(b)];
    for (let i = 0; i < Math.min(x.length, y.length); i++) if (x[i] !== y[i]) return x[i] < y[i] ? -1 : 1;
    return x.length - y.length;
  });
}

/** Stable hash of everything under dir that ships to users (paths + bytes). */
export function contentHash(dir: string): string {
  const h = createHash("sha256");
  for (const f of walk(dir)) {
    if (NO_BUMP_NEEDED.has(path.basename(f)) || f.split(path.sep).includes("__pycache__")) continue;
    h.update(path.relative(dir, f).split(path.sep).join("/") + "\0");
    h.update(readFileSync(f));
    h.update("\0");
  }
  return h.digest("hex").slice(0, 16);
}

export function git(...args: string[]): string | null {
  try {
    return execFileSync("git", args, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
  } catch {
    return null;
  }
}

/** Value of `--name value` in argv, or undefined. */
export function opt(name: string): string | undefined {
  const i = process.argv.indexOf(name);
  return i >= 0 && i < process.argv.length - 1 ? process.argv[i + 1] : undefined;
}

/**
 * The previously published site catalog: the baseline for version-bump checks and "updated" dates.
 * src is a path, a URL, or "auto" (metadata.site + /data/index.json). On Vercel ($VERCEL set) it
 * defaults to "auto", because the build's clone has no origin/main and only shallow history.
 * Returns null if there isn't one yet (first deploy) or it can't be fetched.
 */
export async function loadPrevCatalog(mp: Marketplace, src = opt("--prev-catalog") ?? (process.env.VERCEL ? "auto" : undefined)): Promise<Catalog | null> {
  if (!src) return null;
  if (src === "auto") {
    const site = mp.metadata?.site;
    if (!site) return null;
    src = site.replace(/\/+$/, "") + "/data/index.json";
  }
  try {
    if (/^https?:\/\//.test(src)) {
      const r = await fetch(src, { signal: AbortSignal.timeout(15_000) });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return (await r.json()) as Catalog;
    }
    return JSON.parse(readFileSync(src, "utf8"));
  } catch (e) {
    console.log(`NOTE  no previous catalog at ${src} (${(e as Error).message}); skipping baseline checks`);
    return null;
  }
}
