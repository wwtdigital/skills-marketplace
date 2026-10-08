import type { NextConfig } from "next";

// Every page is prerendered at build time from public/data/index.json (see generateStaticParams).
// The only per-request code is proxy.ts, the team access gate (see lib/access.ts), plus the
// /api/access form handler behind it. agentRules is off so `next dev` doesn't drop AGENTS.md and
// CLAUDE.md into site/ (the repo's CLAUDE.md lives at the root).
const nextConfig: NextConfig = { agentRules: false };

export default nextConfig;
