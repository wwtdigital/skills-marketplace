// Build everything the site serves from the repo, into site/public/ (gitignored):
//   data/index.json            catalog of plugins + skills (rendered by the Next.js pages)
//   downloads/<skill>.skill    zip of each skill folder, for installing one skill by hand
//   downloads/<plugin>.zip     zip of each whole plugin (plugin files at the zip root)
//   marketplace.json           the marketplace with every plugin as an `archive` source pointing at
//                              downloads/<plugin>.zip, so people without GitHub access can run
//                              `/plugin marketplace add https://<site>/marketplace.json`
//
// Usage:  node scripts/build-index.ts [--check] [--prev-catalog SRC] [--site-url URL]
//   --check             build into a temp dir and just report
//   --prev-catalog SRC  published catalog (path, URL, or "auto"; defaults to "auto" on Vercel).
//                       Skills whose content hash is unchanged keep its "updated" date, because
//                       Vercel's shallow clone can't give reliable git dates.
//   --site-url URL      absolute base for marketplace.json archive URLs. Defaults to
//                       metadata.site in production and the deployment's own URL on previews.
import { createHash } from "node:crypto";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { zipSync, type Zippable } from "fflate";
import { REPO_URL, type Catalog, type Plugin, type Skill } from "../lib/catalog.ts";
import {
  contentHash, git, iterSkills, loadMarketplace, loadPluginManifest, loadPrevCatalog, type Marketplace,
  opt, pluginDir, rel, ROOT, walk,
} from "./lib.ts";

const SITE_PUBLIC = path.join(ROOT, "site", "public");
const ZIP_EPOCH = new Date(1980, 0, 2); // local time: zip stores local dates and rejects anything before 1980

const nowIso = () => new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00");

function lastModified(dir: string): string {
  return (git("log", "-1", "--format=%cI", "--", rel(dir)) ?? "").trim() || nowIso();
}

/** Zip dir to dest (entries under arcRoot/, or at the zip root if arcRoot is ""). Returns [bytes, sha256]. */
function zipDir(dir: string, dest: string, arcRoot: string): [number, string] {
  const files: Zippable = {};
  for (const f of walk(dir)) {
    const name = path.basename(f);
    if (name === ".gitkeep" || name === ".DS_Store" || f.split(path.sep).includes("__pycache__")) continue;
    const arc = path.relative(dir, f).split(path.sep).join("/");
    // keep the unix mode (e.g. executable scripts); os: 3 tells unzip to honour it
    files[arcRoot ? `${arcRoot}/${arc}` : arc] = [readFileSync(f), { attrs: (statSync(f).mode & 0xffff) << 16, os: 3 }];
  }
  const data = zipSync(files, { level: 9, mtime: ZIP_EPOCH });
  mkdirSync(path.dirname(dest), { recursive: true });
  writeFileSync(dest, data);
  return [data.byteLength, createHash("sha256").update(data).digest("hex")];
}

function firstParagraph(body: string): string {
  const para: string[] = [];
  for (const line of body.split(/\r?\n/)) {
    const s = line.trim();
    if (!s || s.startsWith("#") || s.startsWith("<!--")) {
      if (para.length) break;
      continue;
    }
    para.push(s);
  }
  return para.join(" ").slice(0, 400);
}

function siteUrl(mp: Marketplace): string {
  const override = opt("--site-url");
  if (override) return override.replace(/\/+$/, "");
  if (process.env.VERCEL_ENV && process.env.VERCEL_ENV !== "production" && process.env.VERCEL_URL)
    return `https://${process.env.VERCEL_URL}`;
  return (mp.metadata?.site ?? "").replace(/\/+$/, "");
}

export function build(out: string, prev: Catalog | null): Catalog {
  const mp = loadMarketplace();
  const dl = path.join(out, "downloads");
  mkdirSync(path.join(out, "data"), { recursive: true });
  mkdirSync(dl, { recursive: true });
  const prevSkills = new Map(prev?.plugins.flatMap((p) => p.skills.map((s) => [s.name, s] as const)) ?? []);
  const base = siteUrl(mp);

  const index: Catalog = {
    marketplace: {
      name: mp.name,
      description: String(mp.description ?? ""),
      version: mp.version ?? "",
      repo: REPO_URL,
      site: base,
      install: `/plugin marketplace add ${REPO_URL.replace("https://github.com/", "")}`,
      generated: nowIso(),
      commit: (git("rev-parse", "--short", "HEAD") ?? "").trim() || (process.env.VERCEL_GIT_COMMIT_SHA ?? "").slice(0, 7),
    },
    plugins: [],
  };
  const archiveEntries: Record<string, unknown>[] = [];

  for (const entry of mp.plugins) {
    const pdir = pluginDir(entry);
    const manifest = loadPluginManifest(pdir) ?? {};
    const skills: Skill[] = [];
    for (const sk of iterSkills(entry)) {
      if (sk.problems.length) continue;
      const [size] = zipDir(sk.dir, path.join(dl, `${sk.name}.skill`), sk.name);
      const digest = contentHash(sk.dir);
      const old = prevSkills.get(sk.name);
      const md = sk.metadata;
      skills.push({
        name: sk.name,
        description: sk.description,
        summary: firstParagraph(sk.body),
        body: sk.body.trim(),
        owner: String(md.owner ?? ""),
        status: (md.status ?? "draft") as Skill["status"],
        version: String(md.version ?? ""),
        connectors: md.connectors ?? [],
        has_scripts: existsSync(path.join(sk.dir, "scripts")),
        has_references: existsSync(path.join(sk.dir, "references")),
        updated: old?.content_hash === digest ? old.updated : lastModified(sk.dir),
        source: `${REPO_URL}/tree/main/${rel(sk.dir)}`,
        download: `downloads/${sk.name}.skill`,
        download_bytes: size,
        content_hash: digest,
      });
    }
    const [psize, sha256] = zipDir(pdir, path.join(dl, `${entry.name}.zip`), "");
    const author = (entry.author ?? manifest.author) as { name?: string } | undefined;
    const plugin: Plugin = {
      name: entry.name,
      displayName: String(entry.displayName ?? manifest.displayName ?? entry.name),
      description: String(entry.description ?? manifest.description ?? ""),
      category: String(entry.category ?? ""),
      tags: (entry.tags ?? manifest.keywords ?? []) as string[],
      version: String(entry.version ?? manifest.version ?? ""),
      author: author?.name ?? "",
      install: `/plugin install ${entry.name}@${mp.name}`,
      source: `${REPO_URL}/tree/main/${rel(pdir)}`,
      download: `downloads/${entry.name}.zip`,
      download_bytes: psize,
      content_hash: contentHash(pdir),
      skills,
    };
    index.plugins.push(plugin);
    archiveEntries.push({ ...entry, source: { source: "archive", url: `${base}/${plugin.download}`, sha256 } });
  }

  writeFileSync(path.join(out, "data", "index.json"), JSON.stringify(index, null, 2) + "\n");
  // Same marketplace (same name, so installs are interchangeable), minus git-only fields.
  const { metadata, ...rest } = mp;
  const { pluginRoot: _unused, ...meta } = metadata ?? {};
  writeFileSync(path.join(out, "marketplace.json"), JSON.stringify({ ...rest, metadata: meta, plugins: archiveEntries }, null, 2) + "\n");
  return index;
}

const check = process.argv.includes("--check");
const prev = await loadPrevCatalog(loadMarketplace());
let idx: Catalog;
if (check) {
  const td = mkdtempSync(path.join(tmpdir(), "catalog-"));
  idx = build(td, prev);
  rmSync(td, { recursive: true, force: true });
} else {
  // clean generated outputs so removed skills disappear
  for (const sub of ["data", "downloads", "marketplace.json"]) rmSync(path.join(SITE_PUBLIC, sub), { recursive: true, force: true });
  idx = build(SITE_PUBLIC, prev);
}
const nSkills = idx.plugins.reduce((a, p) => a + p.skills.length, 0);
console.log(`${check ? "checked" : "built"} index: ${idx.plugins.length} plugins, ${nSkills} skills` +
  (check ? "" : ` → ${rel(SITE_PUBLIC)}/data/index.json, marketplace.json`));
