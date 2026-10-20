# Commands and checks

Everything here assumes you are in the project folder, signed in to `gh` and `vercel`, and
`<slug>` is the repo / project / subdomain name.

## Vercel setup (step 8)

```bash
vercel link --yes --scope wwtd --project <slug>
```

Add the secrets without echoing them. Read them from `.env.local`:

```bash
for envt in production preview; do
  grep '^SITE_PASSWORD' .env.local | cut -d= -f2- | tr -d '\n' | vercel env add SITE_PASSWORD $envt --scope wwtd --sensitive
  grep '^SESSION_SECRET' .env.local | cut -d= -f2- | tr -d '\n' | vercel env add SESSION_SECRET $envt --scope wwtd --sensitive
done
printf '%s' 'https://<slug>.wwtdigital.io' | vercel env add NEXT_PUBLIC_SITE_URL production --scope wwtd
vercel git connect --yes --scope wwtd
vercel domains add <slug>.wwtdigital.io <slug> --scope wwtd
```

Deployment Protection has no CLI switch. Either do it in the dashboard (project, Settings,
Deployment Protection, Vercel Authentication, Disabled) or call the API with the CLI's own token:

```bash
TOKEN=$(node -e 'console.log(JSON.parse(require("fs").readFileSync(process.env.HOME+"/Library/Application Support/com.vercel.cli/auth.json","utf8")).token)')
PID=$(node -p 'require("./.vercel/project.json").projectId'); TEAM=$(node -p 'require("./.vercel/project.json").orgId')
curl -s -X PATCH "https://api.vercel.com/v9/projects/$PID?teamId=$TEAM" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"ssoProtection":null,"passwordProtection":null}' | grep -o '"ssoProtection":[^,]*'
```

Expect `"ssoProtection":null`. Confirm Web Analytics is on the same way: the project JSON
(`GET /v9/projects/$PID?teamId=$TEAM`) should contain a `webAnalytics` object. If it does not,
enable it in the dashboard under the project's Analytics tab.

Optional second domain that redirects to the first:

```bash
vercel domains add <other>.wwtdigital.io <slug> --scope wwtd
curl -s -X PATCH "https://api.vercel.com/v9/projects/$PID/domains/<other>.wwtdigital.io?teamId=$TEAM" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"redirect":"<slug>.wwtdigital.io","redirectStatusCode":308}'
```

## Deploy (step 9)

```bash
vercel deploy --prod --yes --scope wwtd
vercel ls --scope wwtd | head -5
```

## Gate checks (steps 6 and 10)

Set `B` to `http://localhost:<port>` for the local run or `https://<slug>.wwtdigital.io` for
production, and `PW` to the passcode read from `.env.local`. Expected results are in the comments.

```bash
B=https://<slug>.wwtdigital.io
PW=$(grep '^SITE_PASSWORD' .env.local | cut -d= -f2-)
J=$(mktemp)

# 200 and the unlock screen, at the original URL
curl -s -o /tmp/gate.html -w 'home: %{http_code}\n' "$B/"; grep -c 'Passcode' /tmp/gate.html          # 1 or more
grep -oE 'og:(title|url|image)" content="[^"]*"' /tmp/gate.html                                            # three tags, right domain

# Artifact body must not leak without a cookie (pick a phrase that exists only in the artifact)
curl -s "$B/artifact" | grep -c '<SOME PHRASE FROM THE ARTIFACT>'                                           # 0

# Public bits
curl -s -o /dev/null -w 'og image: %{http_code} %{content_type}\n' "$B/opengraph-image"                    # 200 image/png
curl -s "$B/robots.txt"                                                                                     # Disallow: /

# Wrong passcode bounces with an error flag; open-redirect attempt falls back to /
curl -s -o /dev/null -w 'wrong: %{http_code} -> %{redirect_url}\n' -X POST -d 'password=nope&next=/' "$B/api/unlock"   # 303 -> /?error=1
curl -s -o /dev/null -w 'evil next: %{http_code} -> %{redirect_url}\n' -X POST --data-urlencode "password=$PW" -d 'next=//evil.example' "$B/api/unlock"  # 303 -> /

# Right passcode sets the cookie; artifact then served
curl -s -c "$J" -D - -o /dev/null -X POST --data-urlencode "password=$PW" -d 'next=/' "$B/api/unlock" | grep -i '^set-cookie' | sed -E 's/=[^;]*;/=<redacted>;/'   # HttpOnly; Secure (prod); SameSite=lax
curl -s -b "$J" "$B/artifact" | grep -c '<SOME PHRASE FROM THE ARTIFACT>'                                   # 1 or more
curl -s -b "$J" "$B/" | grep -oE '<iframe[^>]*>'                                                            # iframe src="/artifact"

# Tampered cookie gets the unlock screen
curl -s -b 'bp_session=9999999999.AAAA' "$B/" | grep -c 'Passcode'                                          # 1 or more

# Headers on the shell and on the artifact
curl -s -D - -o /dev/null "$B/" | grep -iE 'content-security|strict-transport|x-frame|x-robots'
curl -s -b "$J" -D - -o /dev/null "$B/artifact" | grep -iE 'content-security|cache-control'                 # frame-ancestors 'self'; private, no-store

# Production only: deployment URL is not behind Vercel sign-in
curl -s -o /dev/null -w 'deployment url: %{http_code}\n' "https://<slug>-wwtd.vercel.app/"                 # 200, not 302
rm -f "$J"
```

## Passcode generator

Three words from a list you write for the client plus a two-digit number. Write the list from
things a casual fan or outsider would not guess first (towns, 1980s names, old stadiums,
founders' hometowns), not the mascot or the slogan.

```bash
node -e 'const w=["word1","word2","word3","word4","word5","word6","word7","word8","word9","word10"];const c=require("crypto");const p=()=>w.splice(c.randomInt(w.length),1)[0];console.log(`${p()}-${p()}-${p()}-${c.randomInt(10,99)}`)'
```
