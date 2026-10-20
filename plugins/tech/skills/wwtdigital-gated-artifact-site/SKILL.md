---
name: wwtdigital-gated-artifact-site
description: >
  Host a Claude HTML artifact (a readout, brief, prototype or one-page report) as its own
  password-gated website on the WWTD Vercel team, in a new private repo under the WWTdigital
  GitHub org, at <name>.wwtdigital.io, with link previews (Open Graph), Vercel Analytics and
  security headers already wired up. Use when someone says "host this artifact", "put this HTML
  behind a password", "password-gated site for the client", "landing zone for this readout",
  "share this with the client team on a private link", "get this on wwtdigital.io", or wants a
  Vercel site for a single HTML file the client should see but the public shouldn't. Also use to
  update such a site: swap the HTML, change the passcode, add a domain. Not for publishing a
  page publicly (use publish-page), not for adding login or auth to an existing app, and not for
  multi-page sites or apps with a backend.
metadata:
  owner: scott.cullum@wwt.com
  category: tech
  status: draft
  connectors: []
  version: 0.1.0
---

# WWTDigital Gated Artifact Site

Turns one HTML artifact into a private website in about ten minutes: a new repo from the
`wwtdigital/gated-artifact-site` template, a Vercel project on the WWTD team, a shared passcode,
a `<name>.wwtdigital.io` address, and a verified deployment. The artifact itself is never
edited; it is rendered as-is inside the site's shell, which owns the gate, the link-preview
metadata, the analytics beacon and the security headers.

The first one built this way is `browns-pursuit` (browns-pursuit.wwtdigital.io). Read its repo
if you want to see a finished example, but build new ones from the template, not from it.

## How the template works (so you can explain it and debug it)

- `proxy.ts` checks a signed, HttpOnly cookie on every request. Visitors without one are
  **rewritten**, not redirected, to the unlock screen. The URL they were sent stays in the
  address bar, so Slack and Teams previews read the Open Graph tags from the unlock screen
  and the visitor lands on the right page after entering the passcode. Sessions last 30 days.
- `content/index.html` is the artifact. `app/artifact/route.ts` serves it (gated again, as
  defense in depth) and `app/page.tsx` frames it full-bleed, same origin. It keeps its own
  styles, fonts and CDN scripts because the artifact route carries looser headers than the shell.
- `site.config.ts` holds the three strings that appear in browser tabs and link previews.
  Keep the description generic: anyone who sees the link sees it, passcode or not.
- `SITE_PASSWORD` and `SESSION_SECRET` are environment variables. Rotating the secret signs
  everyone out; rotating the password leaves existing sessions valid until they expire.
- Vercel Analytics comes from `@vercel/analytics` in the layout and is enabled on the project.

## Inputs

Get these before touching anything. Infer what you can from the conversation and the artifact.

1. **The HTML file.** One self-contained file. Check it (step 3) before assuming.
2. **A slug** for the repo, Vercel project and subdomain, kebab-case, for example
   `jersey-mikes-readout`. It is public in the URL, so no internal codenames people would
   not want a client to see.
3. **Name, title and one-line description** for tabs and link previews. Default to the
   artifact's `<title>`, suffixed `| WWT Digital`, and a generic description like
   "Private readout from WWT Digital. Passcode required."
4. **Passcode style.** Default: three words tied to the client or project plus a two-digit
   number, drawn from references that are not the first thing anyone would guess (training
   camp towns and 1980s players, not the mascot). Offer to use the person's own instead.
5. **Second domain?** Only if asked. The first domain is `<slug>.wwtdigital.io`.

## Steps

1. **Preflight.** Run `gh auth status`, `vercel whoami`, `vercel teams ls` and `node -v`.
   You need a GitHub account in the `wwtdigital` org, a Vercel account on the `wwtd` team,
   and Node 24. If any is missing, stop and point the person at the `wwtdigital-onboarding`
   skill or #wwtd-claude-skills; nothing below works without them. Confirm the slug is free:
   `gh repo view wwtdigital/<slug>` should fail.
2. **Create the repo from the template** and clone it next to the person's other work:
   `gh repo create wwtdigital/<slug> --template wwtdigital/gated-artifact-site --private --clone`.
   Then `cd <slug>` and `npm ci`.
3. **Install the artifact.** Copy the HTML to `content/index.html`. Then check it is really
   one file: `grep -oE '(src|href)="(\./|/|[a-z]+/)[^"]*"' content/index.html` should return
   nothing but `href="#..."` anchors. Relative images, scripts or stylesheets will 404 behind
   the gate; inline them or ask for a single-file export. `https://` references (fonts, CDN
   libraries) are fine.
4. **Set the copy.** Edit `name`, `title` and `description` in `site.config.ts`, and set
   `"name"` in `package.json` to the slug.
5. **Generate secrets into `.env.local`** (gitignored). `SESSION_SECRET` is
   `node -e 'console.log(require("crypto").randomBytes(48).toString("base64url"))'`.
   `SITE_PASSWORD` follows input 4. Never print either one in your reply; say where they are.
6. **Check it locally.** `npx next typegen && npx tsc --noEmit && npm run lint`. Then start
   `npm run dev -- --port <free port>` and run the curl checks in
   [references/commands.md](references/commands.md) against it: unlock screen on `/`, no
   artifact text without the cookie, wrong passcode bounces with `?error=1`, right passcode
   sets the cookie and `/artifact` returns the real content. Stop the dev server after.
   Skip the local production build; the Vercel build in step 9 is the production build check,
   and a local one can clobber another Next dev server's output on the same machine.
7. **Commit and push to `main`.** Make sure `.env.local` is not in the commit.
8. **Create the Vercel project and wire it up**, using the commands in
   [references/commands.md](references/commands.md): `vercel link` to a new project named
   `<slug>` on `--scope wwtd`; add `SITE_PASSWORD` and `SESSION_SECRET` as sensitive env vars
   for production and preview; add `NEXT_PUBLIC_SITE_URL=https://<slug>.wwtdigital.io` for
   production; `vercel git connect` so pushes deploy; turn Deployment Protection off (the
   project's own passcode is the access control, and Vercel Authentication would make every
   outside viewer sign in to Vercel); `vercel domains add <slug>.wwtdigital.io <slug>`. The
   `wwtdigital.io` zone is Vercel-managed with a wildcard record, so the domain verifies at once.
9. **Deploy:** `vercel deploy --prod --yes --scope wwtd`, then wait for `vercel ls` to show
   it Ready.
10. **Verify production** with the same curl checks against `https://<slug>.wwtdigital.io`,
    plus: `og:url` in the HTML points at that domain, `/opengraph-image` returns a PNG, a
    tampered cookie gets the unlock screen, and the deployment URL (`<slug>-wwtd.vercel.app`)
    returns 200 rather than a Vercel sign-in redirect. Open the site in a browser once and
    confirm the analytics beacon fires (a POST to a `/.../view` path on the same origin
    returning 200). Take a screenshot of the unlock screen and one of the artifact behind it.
11. **Hand over.** Report the URL, where the passcode lives (`.env.local`, and the Vercel env
    var), and how to update: replace `content/index.html` and push; change `SITE_PASSWORD` in
    Vercel and redeploy. If they want a Slack message for the client team, draft it with the
    passcode left for a separate DM.

## Updating an existing site

- **New version of the artifact:** replace `content/index.html`, commit, push. Or edit the
  file on github.com; Vercel redeploys in about 30 seconds.
- **New passcode:** `vercel env rm SITE_PASSWORD production --yes` then `vercel env add
  SITE_PASSWORD production --sensitive`, same for preview, then redeploy. Update `.env.local`.
- **Extra domain:** `vercel domains add <other>.wwtdigital.io <slug>`, then either leave
  both live or set one to redirect to the other with the API call in the reference file.

## Output

A private repo `github.com/wwtdigital/<slug>`, a Vercel project `<slug>` on the WWTD team with
Deployment Protection off and Web Analytics on, the site live at `https://<slug>.wwtdigital.io`
behind a passcode, and a short report with the verification results and update instructions.

## Guardrails

- Never commit `.env.local`, never paste the passcode or session secret into chat, a commit,
  a README or a Slack draft. Say where they are stored.
- One artifact per site. A second artifact gets its own repo and project.
- Do not touch the `wwtdigital.io` apex, other projects' domains, or any other project's
  Deployment Protection. Only the project you created.
- Leave the production build to Vercel; don't run it locally while another dev server is up.
- If the artifact contains client-confidential material, keep the link-preview description
  generic. The preview card is visible to anyone the link is forwarded to.

## Examples

**User says:** "I've got the Jersey Mike's readout as an HTML artifact in Downloads. Put it
somewhere the client team can see it with a password, on our Vercel, under wwtdigital.io."
**Claude does:** preflight, creates `wwtdigital/jersey-mikes-readout` from the template, copies
the HTML in, sets the copy from its `<title>`, generates a sub-themed passcode and secret,
checks the gate locally, pushes, creates the Vercel project with env vars and
`jersey-mikes-readout.wwtdigital.io`, deploys, verifies with curl and a screenshot, and
reports the URL with the passcode's location.

**User says:** "New version of the Browns brief, same site."
**Claude does:** replaces `content/index.html` in the existing repo, pushes, confirms the
production deployment is Ready and the new content is served behind the gate.
