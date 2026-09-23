# Marketplace site

Next.js (App Router), deployed to Vercel with **Root Directory = `site/`** and Framework Preset =
*Next.js*. Every page is prerendered at build, so nothing runs per request today. It's a full Next.js
app (not `output: "export"`) so route handlers or middleware can be added without a hosting change.

Everything is rendered at build time from `public/data/index.json`, which `scripts/build_index.py`
generates along with `public/downloads/`. CI commits both on every push to `main`, and that push
triggers the Vercel deploy. `vercel.json` sets the cache and download headers for those paths.

- `app/page.tsx`: catalog, install tabs, search and status filter (`components/`)
- `app/skills/[name]/page.tsx`: one page per skill, rendering its SKILL.md body
- `lib/catalog.ts`: catalog types and client-safe helpers. `lib/load.ts` reads the file and is server-only.

Local preview (from the repo root):

```
python3 scripts/build_index.py
cd site && npm ci
npm run dev        # http://localhost:3000
npm run build
npm start          # serve the production build
```
