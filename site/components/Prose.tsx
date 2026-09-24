import type { ReactNode } from "react";
import Markdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { REPO_URL } from "@/lib/catalog";

const SITE = "https://skills-marketplace.wwtdigital.io";

const text = (n: ReactNode): string =>
  typeof n === "string" || typeof n === "number"
    ? String(n)
    : Array.isArray(n)
      ? n.map(text).join("")
      : n && typeof n === "object" && "props" in n
        ? text((n as { props: { children?: ReactNode } }).props.children)
        : "";
export const slug = (n: ReactNode) =>
  text(n)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

/**
 * Links to this site become relative (so they work on previews); repo-relative paths point at
 * GitHub, resolved against `base` (the markdown file's own folder, e.g. a skill's directory), so a
 * skill's `references/x.md` link lands on that skill's file rather than the repo root.
 */
function href(h = "", base = ""): string {
  if (h.startsWith(SITE)) return h.slice(SITE.length) || "/";
  if (/^([a-z]+:|#|\/)/i.test(h)) return h;
  const path = new URL(h, `https://repo.invalid/${base ? base.replace(/\/?$/, "/") : ""}`).pathname;
  return `${REPO_URL}/blob/main${path}`;
}

const components = (base: string): Components => ({
  h2: ({ children }) => <h2 id={slug(children)}>{children}</h2>,
  h3: ({ children }) => <h3 id={slug(children)}>{children}</h3>,
  a: ({ href: h, children }) => {
    const to = href(h, base);
    const external = /^https?:/.test(to);
    return (
      <a href={to} {...(external ? { target: "_blank", rel: "noopener" } : {})}>
        {children}
      </a>
    );
  },
});

/** The `## ` headings of a markdown doc, with the same ids Prose gives them (for a table of contents). */
export function headings(md: string): { id: string; text: string }[] {
  return [...md.matchAll(/^## +(.+)$/gm)].map((m) => {
    const t = m[1].replace(/[`*_]/g, "").trim();
    return { id: slug(t), text: t };
  });
}

/** Render repo markdown (SKILL.md bodies, CONTRIBUTING.md) with GitHub-flavored extensions. */
export function Prose({ children, base = "" }: { children: string; base?: string }) {
  return (
    <article className="prose">
      <Markdown remarkPlugins={[remarkGfm]} components={components(base)}>
        {children}
      </Markdown>
    </article>
  );
}
