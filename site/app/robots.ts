import type { MetadataRoute } from "next";

// The site is for the team; keep it out of search engines. vercel.json also sends X-Robots-Tag.
export default function robots(): MetadataRoute.Robots {
  return { rules: { userAgent: "*", disallow: "/" } };
}
