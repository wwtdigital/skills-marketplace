import { NextRequest, NextResponse } from "next/server";
import { COOKIE, accessMode, bearer, cookieAttrs, cookieValueFor, isValidCookie, isValidToken } from "@/lib/access";

// The team access gate. Runs before every route and every public/ file except the few excluded in
// `config.matcher` below. Three ways in, all with the same key (see lib/access.ts):
//   1. `Authorization: Bearer <key>`: Claude Code sends this from the extraKnownMarketplaces entry,
//      on marketplace.json and on every zip download; the build scripts and curl use it too.
//   2. The wwtd_access cookie, derived from the key.
//   3. `?key=<key>` on any URL (the link pinned in Slack): sets the cookie and redirects to the same
//      URL without the query.
// Unauthenticated machine requests (marketplace.json, downloads, data) get a plain 401 so a CLI
// shows something useful; everything else is rewritten to the /access form with the URL kept.

const MACHINE_PATHS = [/^\/marketplace\.json$/, /^\/downloads\//, /^\/data\//];

const noStore = (res: NextResponse) => {
  res.headers.set("Cache-Control", "private, no-store");
  return res;
};

export default async function proxy(req: NextRequest) {
  const mode = accessMode();
  if (mode === "open") return NextResponse.next();
  const url = req.nextUrl;
  const https = url.protocol === "https:";

  // 3. Slack link
  const key = url.searchParams.get("key");
  if (key !== null && mode === "gated" && (await isValidToken(key))) {
    const clean = url.clone();
    clean.searchParams.delete("key");
    const res = NextResponse.redirect(clean, 302);
    res.cookies.set(cookieAttrs(await cookieValueFor(key), https));
    return noStore(res);
  }

  // 1. Bearer, 2. cookie
  if (mode === "gated") {
    if (await isValidToken(bearer(req.headers.get("authorization")))) return NextResponse.next();
    if (await isValidCookie(req.cookies.get(COOKIE)?.value)) return NextResponse.next();
  }

  // Not authenticated.
  const machine = MACHINE_PATHS.some((re) => re.test(url.pathname));
  const browser = (req.headers.get("accept") ?? "").includes("text/html");
  if (machine && !browser) {
    const body =
      mode === "closed"
        ? "Site access is not configured (SITE_ACCESS_TOKENS is unset).\n"
        : "Unauthorized. Send the team access key as `Authorization: Bearer <key>`.\n";
    return new NextResponse(body, {
      status: 401,
      headers: {
        "content-type": "text/plain; charset=utf-8",
        "www-authenticate": 'Bearer realm="wwtdigital-skills"',
        "cache-control": "private, no-store",
      },
    });
  }
  // A browser (including a download click with an expired cookie) gets the form; the address bar
  // keeps the URL it asked for, and the form returns there after sign-in.
  return noStore(NextResponse.rewrite(new URL("/access", req.url)));
}

export const config = {
  // Everything except Next's own static assets, Vercel Analytics, the icon, robots.txt, and the
  // access form itself. Must be one static constant: Next compiles it at build time.
  matcher: ["/((?!_next/static|_next/image|_vercel|icon\\.svg|favicon\\.ico|robots\\.txt|access|api/access).*)"],
};
