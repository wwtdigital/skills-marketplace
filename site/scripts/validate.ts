// Validate marketplace.json, every plugin.json, and every SKILL.md.
//
// Usage:  node scripts/validate.ts [--strict] [--base REF] [--prev-catalog SRC]
//   --strict            treat warnings as errors (npm run build uses this, so it gates deploys)
//   --base REF          require version bumps for anything changed since git REF, e.g.
//                       --base origin/main. Compares the working tree, so uncommitted changes count.
//   --prev-catalog SRC  require version bumps for anything whose content differs from a published
//                       site catalog (path, URL, or "auto" for the live site). Defaults to "auto" on
//                       Vercel, whose clone has no origin/main to diff against.
// Exit code 1 on any error.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import {
  contentHash, DISCIPLINES, git, iterSkills, KEBAB, loadMarketplace, loadPluginManifest,
  loadPrevCatalog, type Marketplace, type MarketplaceEntry, NO_BUMP_NEEDED, opt, parseSkillMd,
  pluginDir, rel, type SkillSource, STATUSES, walk,
} from "./lib.ts";

const SECRET_PATTERNS = [
  /(api[_-]?key|secret|token|password)\s*[:=]\s*['"][^'"]{8,}/i,
  /xox[baprs]-[A-Za-z0-9-]{10,}/, // Slack
  /ghp_[A-Za-z0-9]{36}/, // GitHub PAT
  /glpat-[A-Za-z0-9-]{20,}/, // GitLab PAT
  /AKIA[0-9A-Z]{16}/, // AWS
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
];
const BINARY = new Set([".png", ".jpg", ".jpeg", ".gif", ".pdf", ".pptx", ".docx", ".xlsx", ".zip"]);

const errors: string[] = [];
const warnings: string[] = [];
const notes: string[] = [];
const err = (m: string) => errors.push(m);
const warn = (m: string) => warnings.push(m);
const list = (xs: string[]) => `[${xs.join(", ")}]`;

function checkMarketplace(mp: Marketplace) {
  for (const k of ["name", "owner", "plugins"]) if (!(k in mp)) err(`marketplace.json: missing required field '${k}'`);
  if (mp.owner && !mp.owner.name) err("marketplace.json: owner.name is required");
  if (!KEBAB.test(mp.name ?? "")) err(`marketplace.json: name '${mp.name}' must be kebab-case`);
  const names = (mp.plugins ?? []).map((p) => p.name);
  const dups = [...new Set(names.filter((n, i) => names.indexOf(n) !== i))].sort();
  if (dups.length) err(`marketplace.json: duplicate plugin names ${list(dups)}`);
  for (const [from, to] of Object.entries(mp.renames ?? {}))
    if (to !== null && !names.includes(to)) err(`marketplace.json: renames['${from}'] -> '${to}' is not a listed plugin`);
}

function checkPlugin(entry: MarketplaceEntry) {
  const n = entry.name ?? "?";
  if (!KEBAB.test(n)) err(`plugin '${n}': name must be kebab-case`);
  if (entry.source === undefined) return err(`plugin '${n}': missing 'source'`);
  const pdir = pluginDir(entry);
  if (!existsSync(pdir)) return err(`plugin '${n}': source directory ${rel(pdir)} does not exist`);
  if (String(entry.source).includes("..")) err(`plugin '${n}': source must not escape the marketplace root`);
  const manifest = loadPluginManifest(pdir);
  if (!manifest) err(`plugin '${n}': missing .claude-plugin/plugin.json`);
  else {
    if (manifest.name !== n) err(`plugin '${n}': plugin.json name '${manifest.name}' does not match marketplace entry`);
    if (!("version" in manifest)) warn(`plugin '${n}': plugin.json has no version (users won't get pinned updates)`);
  }
  if (!existsSync(path.join(pdir, "README.md"))) warn(`plugin '${n}': no README.md`);
  if (!entry.description) warn(`plugin '${n}': no description in marketplace entry`);

  const skills = iterSkills(entry);
  if (!skills.length) notes.push(`plugin '${n}': contains no skills yet`); // expected for new disciplines
  for (const sk of skills) {
    for (const p of sk.problems) err(`${n}/${sk.name}: ${p}`);
    if (sk.problems.length && !sk.description) continue;
    checkSkill(n, sk);
  }
}

function checkSkill(plugin: string, sk: SkillSource) {
  const tag = `${plugin}/${sk.name}`;
  if (!KEBAB.test(sk.name)) err(`${tag}: skill folder must be kebab-case`);
  const d = sk.description;
  if (!d) err(`${tag}: description is required`);
  else {
    if (d.length > 1024) err(`${tag}: description is ${d.length} chars (max 1024)`);
    if (d.length < 80) warn(`${tag}: description is short (${d.length} chars) — say when to use it, with trigger phrases`);
    if (!/\buse (this |it )?when\b|\btrigger/i.test(d)) warn(`${tag}: description doesn't say when to use it ('Use when …')`);
  }
  const md = sk.metadata;
  if (!Object.keys(md).length) warn(`${tag}: no metadata block (owner, discipline, status)`);
  else {
    const owner = String(md.owner ?? "");
    if (!owner.endsWith("@wwt.com")) err(`${tag}: metadata.owner must be a @wwt.com address (got '${owner}')`);
    if (!DISCIPLINES.includes(md.discipline as string)) err(`${tag}: metadata.discipline must be one of ${list(DISCIPLINES)}`);
    if (!STATUSES.includes(md.status as string)) err(`${tag}: metadata.status must be one of ${list(STATUSES)}`);
    if (!("version" in md)) warn(`${tag}: metadata.version missing`);
  }
  const lines = sk.body.split("\n").length - 1;
  if (lines > 250) warn(`${tag}: SKILL.md body is ${lines} lines — move detail into references/`);
  const body = sk.body.toLowerCase();
  if (!body.includes("verif") && !body.includes("check")) warn(`${tag}: no verification step mentioned in the workflow`);
  // secrets scan across the whole skill folder
  for (const f of walk(sk.dir)) {
    if (BINARY.has(path.extname(f).toLowerCase())) continue;
    const txt = readFileSync(f, "utf8");
    const hit = SECRET_PATTERNS.find((p) => p.test(txt));
    if (hit) err(`${tag}: possible secret in ${rel(f)} (pattern ${hit.source.slice(0, 30)}…)`);
  }
}

// ---- version bumps -------------------------------------------------------------------------
// plugin.json `version` is what Claude Code compares to decide whether installed users get an
// update, so any shipped change to a plugin without a bump silently never reaches them.

function semver(v: unknown): number[] | null {
  const m = /^(\d+)\.(\d+)\.(\d+)$/.exec(String(v ?? "").trim());
  return m ? m.slice(1).map(Number) : null;
}

function bumped(oldV: unknown, newV: unknown): boolean {
  const [o, n] = [semver(oldV), semver(newV)];
  if (!o || !n) return String(newV) !== String(oldV);
  for (let i = 0; i < 3; i++) if (n[i] !== o[i]) return n[i] > o[i];
  return false;
}

const skillVersion = (md: string | null) => {
  try {
    return md === null ? undefined : ((parseSkillMd(md)[0].metadata ?? {}) as { version?: unknown }).version;
  } catch {
    return undefined;
  }
};

function checkVersionBumps(mp: Marketplace, base: string) {
  const mb = (git("merge-base", base, "HEAD") ?? "").trim();
  if (!mb) return err(`--base ${base}: not a git ref this checkout knows (fetch it first)`);
  const changed = new Set([
    ...(git("diff", "--name-only", mb) ?? "").split("\n"),
    ...(git("ls-files", "--others", "--exclude-standard") ?? "").split("\n"),
  ].filter(Boolean));
  const atBase = (p: string) => git("show", `${mb}:${p}`);

  const baseMp = atBase(".claude-plugin/marketplace.json");
  if (baseMp) {
    const old = JSON.parse(baseMp) as Marketplace;
    if (!sameNames(old.plugins, mp.plugins) && !bumped(old.version, mp.version))
      err(`marketplace.json: plugins were added, removed or renamed but version is still ${mp.version} (bump it)`);
  }
  for (const entry of mp.plugins ?? []) {
    const prel = rel(pluginDir(entry));
    const shipped = [...changed].filter((f) => f.startsWith(prel + "/") && !NO_BUMP_NEEDED.has(path.basename(f))).sort();
    if (!shipped.length) continue;
    const oldManifest = atBase(`${prel}/.claude-plugin/plugin.json`);
    if (oldManifest === null) continue; // new plugin: nothing installed to update
    const oldV = JSON.parse(oldManifest).version;
    const newV = loadPluginManifest(pluginDir(entry))?.version;
    if (!bumped(oldV, newV))
      err(`plugin '${entry.name}': ${shipped.length} file(s) changed since ${base} (e.g. ${shipped[0]}) but plugin.json ` +
        `version ${newV} isn't above ${oldV} — installed users won't get the change until it's bumped`);
    for (const sk of iterSkills(entry)) {
      const srel = rel(sk.dir);
      if (sk.problems.length || !shipped.some((f) => f.startsWith(srel + "/"))) continue;
      const oldMd = atBase(`${srel}/SKILL.md`);
      if (oldMd === null) continue; // new skill
      const oldSv = skillVersion(oldMd);
      if (oldSv !== undefined && !bumped(oldSv, sk.metadata.version))
        err(`${entry.name}/${sk.name}: changed since ${base} but metadata.version ${sk.metadata.version} isn't above ${oldSv}`);
    }
  }
}

function checkAgainstCatalog(mp: Marketplace, prev: NonNullable<Awaited<ReturnType<typeof loadPrevCatalog>>>) {
  const where = "the published catalog";
  if (!sameNames(prev.plugins, mp.plugins) && !bumped(prev.marketplace?.version, mp.version))
    err(`marketplace.json: plugins were added, removed or renamed since ${where} but version is still ${mp.version} (bump it)`);
  const oldPlugins = new Map(prev.plugins.map((p) => [p.name, p]));
  for (const entry of mp.plugins ?? []) {
    const old = oldPlugins.get(entry.name);
    const pdir = pluginDir(entry);
    if (!old?.content_hash || !existsSync(pdir)) continue; // new plugin, or a catalog from before hashes existed
    const newV = loadPluginManifest(pdir)?.version;
    if (contentHash(pdir) !== old.content_hash && !bumped(old.version, newV))
      err(`plugin '${entry.name}': content changed since ${where} but plugin.json version ${newV} isn't above ` +
        `${old.version} — installed users won't get the change until it's bumped`);
    const oldSkills = new Map(old.skills.map((s) => [s.name, s]));
    for (const sk of iterSkills(entry)) {
      const o = oldSkills.get(sk.name);
      if (sk.problems.length || !o?.content_hash) continue;
      if (contentHash(sk.dir) !== o.content_hash && !bumped(o.version, sk.metadata.version))
        err(`${entry.name}/${sk.name}: changed since ${where} but metadata.version ${sk.metadata.version} isn't above ${o.version}`);
    }
  }
}

function sameNames(a: { name: string }[] = [], b: { name: string }[] = []) {
  const [x, y] = [new Set(a.map((p) => p.name)), new Set(b.map((p) => p.name))];
  return x.size === y.size && [...x].every((n) => y.has(n));
}

async function main(): Promise<number> {
  const strict = process.argv.includes("--strict");
  const base = opt("--base");
  const mp = loadMarketplace();
  checkMarketplace(mp);
  for (const entry of mp.plugins ?? []) checkPlugin(entry);
  // skill names must be unique marketplace-wide: downloads and site routes are keyed by name alone
  const seen = new Map<string, string>();
  for (const entry of mp.plugins ?? []) {
    if (entry.source === undefined || !existsSync(pluginDir(entry))) continue;
    for (const sk of iterSkills(entry)) {
      if (seen.has(sk.name)) err(`${entry.name}/${sk.name}: skill name already used in plugin '${seen.get(sk.name)}'`);
      else seen.set(sk.name, entry.name);
    }
  }
  if (base) checkVersionBumps(mp, base);
  const prev = await loadPrevCatalog(mp);
  if (prev) checkAgainstCatalog(mp, prev);

  for (const n of notes) console.log(`NOTE  ${n}`);
  for (const w of warnings) console.log(`WARN  ${w}`);
  for (const e of errors) console.log(`ERROR ${e}`);
  const withSource = (mp.plugins ?? []).filter((e) => e.source !== undefined && existsSync(pluginDir(e)));
  const nSkills = withSource.reduce((a, e) => a + iterSkills(e).length, 0);
  console.log(`\n${mp.plugins?.length ?? 0} plugins, ${nSkills} skills — ${errors.length} errors, ${warnings.length} warnings`);
  return errors.length || (strict && warnings.length) ? 1 : 0;
}

process.exitCode = await main();
