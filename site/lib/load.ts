// Server-only: reads the generated catalog from disk at build time.
import { readFileSync } from "node:fs";
import path from "node:path";
import type { Catalog } from "./catalog";

/** Read the generated catalog at build time. Returns null if scripts/build-index.ts hasn't run. */
export function loadCatalog(): Catalog | null {
  try {
    return JSON.parse(readFileSync(path.join(process.cwd(), "public", "data", "index.json"), "utf8"));
  } catch {
    return null;
  }
}

export function findSkill(catalog: Catalog | null, name: string) {
  for (const plugin of catalog?.plugins ?? []) {
    const skill = plugin.skills.find((s) => s.name === name);
    if (skill) return { plugin, skill };
  }
  return null;
}
