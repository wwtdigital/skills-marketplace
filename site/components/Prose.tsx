import type { ReactNode } from "react";
import Markdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { REPO_URL } from "@/lib/catalog";
import { headings, slug } from "@/lib/markdown";

export { headings } from "@/lib/markdown";

const SITE = "https://skills-marketplace.wwtdigital.io";

const text = (n: ReactNode): string =>
  typeof n === "string" || typeof n === "number"
    ? String(n)
    : Array.isArray(n)
      ? n.map(text).join("")
      : n && typeof n === "object" && "props" in n
        ? text((n as { props: { children?: ReactNode } }).props.children)
        : "";

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

// Heading ids come from lib/markdown's headings() of the same source, looked up by the line the
// heading sits on, so a TOC built from the source text links to exactly these ids (duplicates get
// -2, -3…). The slug of the rendered text is only the fallback for a heading the scan didn't see.
const components = (base: string, ids: Map<number, string>): Components => {
  const id = (line: number | undefined, children: ReactNode) => (line && ids.get(line)) || slug(text(children));
  return {
    h2: ({ children, node }) => <h2 id={id(node?.position?.start.line, children)}>{children}</h2>,
    h3: ({ children, node }) => <h3 id={id(node?.position?.start.line, children)}>{children}</h3>,
    a: ({ href: h, children }) => {
      const to = href(h, base);
      const external = /^https?:/.test(to);
      return (
        <a href={to} {...(external ? { target: "_blank", rel: "noopener" } : {})}>
          {children}
        </a>
      );
    },
  };
};

/** Render repo markdown (SKILL.md bodies, CONTRIBUTING.md) with GitHub-flavored extensions. */
export function Prose({ children, base = "" }: { children: string; base?: string }) {
  const ids = new Map(headings(children).map((h) => [h.line, h.id]));
  return (
    <article className="prose">
      <Markdown remarkPlugins={[remarkGfm]} components={components(base, ids)}>
        {children}
      </Markdown>
    </article>
  );
}
