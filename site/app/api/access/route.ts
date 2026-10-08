import { NextRequest, NextResponse } from "next/server";
import { accessMode, cookieAttrs, cookieValueFor, isValidToken, safeNext } from "@/lib/access";

// Receives the /access form. A valid key sets the cookie and sends the browser on to the page it
// wanted (303 so the follow-up is a GET); anything else goes back to the form with ?error=1.

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const key = String(form.get("key") ?? "").trim();
  const next = safeNext(String(form.get("next") ?? "") || refererPath(req));

  if (accessMode() !== "gated" || !(await isValidToken(key))) {
    const back = new URL("/access", req.url);
    back.searchParams.set("error", "1");
    back.searchParams.set("next", next);
    return noStore(NextResponse.redirect(back, 303));
  }
  const res = NextResponse.redirect(new URL(next, req.url), 303);
  res.cookies.set(cookieAttrs(await cookieValueFor(key), req.nextUrl.protocol === "https:"));
  return noStore(res);
}

export function GET(req: NextRequest) {
  return NextResponse.redirect(new URL("/access", req.url), 303);
}

// With JavaScript off the hidden `next` field is empty; the Referer still says which gated page the
// form was shown on (the proxy rewrites, so the browser's URL is the page the visitor wanted).
function refererPath(req: NextRequest): string {
  try {
    const ref = new URL(req.headers.get("referer") ?? "");
    if (ref.origin !== req.nextUrl.origin || ref.pathname === "/access") return "/";
    return ref.pathname + ref.search;
  } catch {
    return "/";
  }
}

const noStore = (res: NextResponse) => {
  res.headers.set("Cache-Control", "private, no-store");
  return res;
};
