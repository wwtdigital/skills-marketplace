// The team access key: one shared secret that gates the whole site (pages, marketplace.json, downloads).
// Shared by proxy.ts, the /api/access route handler, the home page (which bakes the key into the
// Claude Code install snippet) and the build scripts (which send it when reading the live catalog).
// Web Crypto only, no node:fs, so it can run anywhere Next runs it.
//
// SITE_ACCESS_TOKENS is a comma-separated list so two keys can be live during a rotation:
// set "new,old", redeploy, tell the team, drop "old" a week later, redeploy. The browser cookie is
// derived from the key, so dropping a key logs its holders out without any further work.

export const COOKIE = "wwtd_access";
export const COOKIE_MAX_AGE = 60 * 60 * 24 * 90; // ~90 days
// Version tag inside the cookie derivation. Bumping it (v1 -> v2) invalidates every cookie at once.
const DERIVE_PREFIX = "wwtd-access-v1|";

export function tokens(env = process.env.SITE_ACCESS_TOKENS): string[] {
  return (env ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export const firstToken = (): string | null => tokens()[0] ?? null;

/**
 * "gated": keys are configured, check every request.
 * "closed": on Vercel with no keys: fail closed, nothing is served.
 * "open": local run with no keys: serve everything, warn once.
 */
let warned = false;
export function accessMode(): "gated" | "closed" | "open" {
  if (tokens().length) return "gated";
  if (process.env.VERCEL) return "closed";
  if (!warned) {
    warned = true;
    console.warn("SITE_ACCESS_TOKENS is not set; the site is open (local run only).");
  }
  return "open";
}

async function sha256Hex(s: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

// Both inputs are 64-char hex digests at every call site, so the length check leaks nothing useful.
function equalConstTime(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

/** The cookie value for a key: one-way, so a cookie never reveals the key and dies with it. */
export const cookieValueFor = (token: string): Promise<string> => sha256Hex(DERIVE_PREFIX + token);

/** Is this a currently valid key? Hashes both sides so the compare is constant-time for any input. */
export async function isValidToken(candidate: string | null | undefined): Promise<boolean> {
  if (!candidate) return false;
  const c = await sha256Hex(candidate);
  let ok = false;
  for (const t of tokens()) ok = equalConstTime(c, await sha256Hex(t)) || ok; // no early exit
  return ok;
}

/** Is this cookie value derived from a currently valid key? */
export async function isValidCookie(value: string | null | undefined): Promise<boolean> {
  if (!value) return false;
  let ok = false;
  for (const t of tokens()) ok = equalConstTime(value, await cookieValueFor(t)) || ok;
  return ok;
}

/** The token from an `Authorization: Bearer <token>` header, or null. */
export const bearer = (header: string | null): string | null => /^Bearer\s+(.+)$/i.exec(header ?? "")?.[1]?.trim() ?? null;

/** A same-origin path to return to after sign-in: must start with "/" but not "//" or "/\". Else "/". */
export function safeNext(raw: string | null | undefined): string {
  const s = (raw ?? "").trim();
  return s.startsWith("/") && !/^\/[\/\\]/.test(s) && s.length < 2048 ? s : "/";
}

export const cookieAttrs = (value: string, secure: boolean) => ({
  name: COOKIE,
  value,
  httpOnly: true,
  secure,
  sameSite: "lax" as const,
  path: "/",
  maxAge: COOKIE_MAX_AGE,
});
