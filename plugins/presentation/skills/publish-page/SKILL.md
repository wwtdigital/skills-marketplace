---
name: publish-page
description: >
  Publish an HTML page, report or prototype as a shareable, access-controlled link through the
  team's artifact publisher (the artifact-publisher MCP server bundled with this plugin), and
  manage who can open it: password gate, expiry, per-person share links, revocation. Use when
  someone says "publish this", "make this a shareable link", "send the client a link to this
  report", "put this page somewhere people can open it", "who has access to this page" or
  "revoke that share". Not for Claude.ai Artifacts (use the Artifact tool), for deploying apps
  or anything with a backend, or for anything that isn't a single self-contained HTML or
  Markdown page.
metadata:
  owner: scott.cullum@wwt.com
  category: presentation
  status: draft
  connectors: [artifact-publisher]
  version: 0.1.0
---

# Publish Page

Turns a finished page into a link someone outside this conversation can open, with the access
the person actually wants. The publisher takes one self-contained HTML or Markdown file, gates
it behind a password by default, and can hand named recipients their own revocable links.
The output is one line: the URL, who can open it, and anything the person has to pass along.

## Inputs

- The page: a file path or the page just built. One file, self-contained (CSS and JS inline,
  images as data URIs or absolute URLs). The server takes the content as a string, so there is
  no way to ship a folder of assets.
- Who should be able to open it. Ask before publishing; don't assume.
- A filename (it becomes the slug in the URL), and whether the link should expire.

## Steps

1. Connector check. The tools are `publish_artifact`, `share_artifact`, `list_artifacts`,
   `list_shares`, `update_gate`, `revoke_share` and `delete_artifact`. If they aren't
   available, or a call comes back asking to sign in, the artifact publisher isn't connected:
   tell the person to run `/mcp` in Claude Code (or accept the sign-in prompt in the Claude
   app) and sign in to `artifact-publisher`, then stop.
2. Confirm what's being published. Exactly one file. Check it for relative asset references
   (`href="./…"`, `src="images/…"`, local `<script src>`), and inline them or say the page
   needs to be self-contained before it can go up. Scan for credentials, API keys, internal
   hostnames and client data. If any are there, name them and ask whether they should leave
   the building before going on.
3. Ask who should open it, before publishing. The access model below is what the tool
   descriptions say; if the tools you see offer different gate options, go by those and tell
   the person. From most to least restrictive:
   - Password gate (the default). `publish_artifact` generates a password if none is given
     and returns it once; it cannot be retrieved later. WWT teammates can always open any
     artifact by signing in with Slack, regardless of gate or shares.
   - Named people: keep the password gate and give each person their own link with
     `share_artifact` (recipient email or name, optional `expires_in_days`). Each link is
     revocable on its own. This is the right choice for clients.
   - Expiry: `expires_in_days` on the publish. After expiry everyone, WWT included, sees an
     expired page, and a daily job takes the artifact offline permanently. Offer it for
     anything time-boxed (a review window, a demo).
   - Public (`public: true`): only when the person explicitly asks for no gate. Repeat back
     that anyone with the URL can open it, and get a yes.
   Default to the most restrictive option that does the job.
4. Confirm before the publish call, in one line: filename, gate, expiry, recipients.
   Publishing is outward-facing, so wait for a yes. If the slug already exists (check with
   `list_artifacts` when unsure), say that this republishes over it and keeps its password.
5. Publish: `publish_artifact` with `content`, `filename` (no extension), `content_type`
   (`html` or `markdown`), and `password`, `public` or `expires_in_days` as agreed. Keep the
   returned URL and password. The URL goes live 20 to 60 seconds later.
6. Sharing: for each named recipient, `share_artifact` with the slug and `recipient`. Keep
   each returned link paired with its recipient.
7. Verify. Call `list_artifacts` and check the new slug is listed with the expected gate state
   (password, expiry). If shares were created, call `list_shares` for the slug and check each
   recipient is present with status `valid`. There is no tool that fetches the page itself, so
   don't claim it renders; if it matters, the person opens the link after a minute. If the slug
   or a share isn't listed, or a call fails, say so plainly instead of reporting success.
8. Report in one line: URL, access setting, the password if one was generated (with a note
   that it can't be retrieved later), expiry if set. Then each share link on its own line
   with the recipient's name.

### Managing a page that's already published

- "Who has access": `list_shares` for the slug. Present one line per recipient, leading with
  whether they've opened it and when.
- "Revoke that share": `list_shares` to get the share id, confirm the recipient by name, then
  `revoke_share` with the slug and `grant_id`. It takes effect on their next request.
- Change the password or expiry: `update_gate`. Passwords can be rotated, not removed;
  `clear_expiry: true` removes an expiry. Omit anything that should stay as it is.
- Take it down: `delete_artifact`. Only a developer can restore it, so confirm first.
- Don't guess slugs. `list_artifacts` shows what the person has published.

## Output

One line with the URL and the access setting, plus the password and expiry when they apply,
then one line per recipient link. Nothing else is needed; the person will paste this.

## Guardrails

- Never publish content with credentials, keys or client data unless the person has confirmed
  the audience after seeing what's in it.
- Never widen access (`public: true`, adding recipients, clearing an expiry) and never revoke
  or delete without explicit confirmation in the same conversation. Confirmation for one action
  doesn't carry over to the next.
- Always confirm before `publish_artifact`, even when the page was built in this conversation.
- The generated password goes in the reply to the person and nowhere else: not in the page,
  not in a message drafted to a recipient.
- Don't republish over an existing slug unless the person means to update that page.

## Examples

**User says:** "Publish this report so I can send it to the client."
**Claude does:** Checks the publisher tools are available, confirms the report is one
self-contained HTML file with nothing sensitive in it, asks who at the client should get it and
whether the link should expire, confirms the plan in one line, publishes with the default
password gate, creates one share link per named person, verifies with `list_artifacts` and
`list_shares`, and returns the URL, the password and each person's link.

**User says:** "Who has access to the page I published yesterday, and has anyone opened it?"
**Claude does:** Finds the slug with `list_artifacts`, calls `list_shares`, and answers with one
line per recipient: viewed or not, when, and whether the link is still valid.

**Should not trigger:** "Make this dashboard an artifact so I can look at it." That's a
Claude.ai Artifact for the person's own use, not a published, access-controlled page.
