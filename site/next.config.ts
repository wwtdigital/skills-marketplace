import type { NextConfig } from "next";

// Every page is prerendered at build time from public/data/index.json (see generateStaticParams),
// so there's no per-request work today. Kept as a full Next.js app on Vercel so route handlers or
// middleware (download tracking, SSO) can be added without a hosting change.
const nextConfig: NextConfig = {};

export default nextConfig;
