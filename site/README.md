# Marketplace site

Next.js (App Router), deployed to Vercel with **Root Directory = `site/`** and Framework Preset =
*Next.js*. Every page is prerendered at build, so nothing runs per request today. It's a full Next.js
app (not `output: "export"`) so route handlers or middleware can be added without a hosting change.

Everything is rendered at build time from `public/data/index.json`. `scripts/catalog.sh` runs
before `next dev` and `next build` and generates that file plus `public/downloads/`, both
gitignored. It sets up a Python venv with PyYAML in `.pyenv/` and runs the repo's
`scripts/validate.py` (build only, strict) and `scripts/build_index.py`. So the Vercel build is also
the repo's CI: an invalid skill fails the deploy. The build reads files outside `site/`, so the
Vercel project needs "Include files outside the root directory" enabled (the default).
`vercel.json` sets the cache and download headers for the generated paths.

- `app/page.tsx`: catalog, install tabs, search and status filter (`components/`)
- `app/skills/[name]/page.tsx`: one page per skill, rendering its SKILL.md body
- `lib/catalog.ts`: catalog types and client-safe helpers. `lib/load.ts` reads the file and is server-only.

Local preview:

```
cd site && npm ci
npm run dev        # http://localhost:3000
npm run build
npm start          # serve the production build
```
