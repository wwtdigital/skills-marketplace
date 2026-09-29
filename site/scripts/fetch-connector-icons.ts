// Download connector logos into site/public/connectors/ (committed, so the site never calls out at
// runtime) and write lib/connector-icons.json, which ConnectorTag reads to know which exist.
// Logos are each service's own favicon via Google's favicon service. Run by hand when a
// connector is added to CONNECTOR_ICON_SOURCES, then look at the results before committing:
// some sites only have a generic favicon.
//
// Usage:  node scripts/fetch-connector-icons.ts
import { mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { CONNECTOR_ICON_SOURCES } from "../lib/catalog.ts";

const site = path.resolve(import.meta.dirname, "..");
const out = path.join(site, "public", "connectors");
const SIZE = 64;

// Sniff the type from the bytes: the service returns JPEG for a few sites.
function ext(b: Uint8Array): string | null {
  if (b[0] === 0x89 && b[1] === 0x50) return "png";
  if (b[0] === 0xff && b[1] === 0xd8) return "jpg";
  if (b[0] === 0x3c) return "svg";
  if (b[0] === 0x52 && b[8] === 0x57) return "webp";
  return null;
}

mkdirSync(out, { recursive: true });
for (const f of readdirSync(out)) rmSync(path.join(out, f));
const manifest: Record<string, string> = {};
let failed = 0;
for (const [name, url] of Object.entries(CONNECTOR_ICON_SOURCES)) {
  const q = new URLSearchParams({ client: "SOCIAL", type: "FAVICON", fallback_opts: "TYPE,SIZE,URL", url, size: String(SIZE) });
  const res = await fetch(`https://t2.gstatic.com/faviconV2?${q}`);
  const bytes = new Uint8Array(await res.arrayBuffer());
  const e = ext(bytes);
  // A 404 still carries Google's generic globe; don't keep it.
  if (!res.ok || !e) {
    console.error(`FAIL  ${name}: ${url} -> ${res.status}`);
    failed++;
    continue;
  }
  const file = `${name}.${e}`;
  writeFileSync(path.join(out, file), bytes);
  manifest[name] = file;
  console.log(`ok    ${name.padEnd(16)} ${file.padEnd(22)} ${bytes.length} B`);
}
const sorted = Object.fromEntries(Object.entries(manifest).sort(([a], [b]) => a.localeCompare(b)));
writeFileSync(path.join(site, "lib", "connector-icons.json"), JSON.stringify(sorted, null, 2) + "\n");
if (failed) process.exit(1);
