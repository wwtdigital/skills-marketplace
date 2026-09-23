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
const slug = (n: ReactNode) =>
  text(n)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

/** Links to this site become relative (so they work on previews); repo-relative paths point at GitHub. */
function href(h = ""): string {
  if (h.startsWith(SITE)) return h.slice(SITE.length) || "/";
  if (/^([a-z]+:|#|\/)/i.test(h)) return h;
  return `${REPO_URL}/blob/main/${h.replace(/^(\.\.\/)+|^\.\//, "")}`;
}

const components: Components = {
  h2: ({ children }) => <h2 id={slug(children)}>{children}</h2>,
  h3: ({ children }) => <h3 id={slug(children)}>{children}</h3>,
  a: ({ href: h, children }) => {
    const to = href(h);
    const external = /^https?:/.test(to);
    return (
      <a href={to} {...(external ? { target: "_blank", rel: "noopener" } : {})}>
        {children}
      </a>
    );
  },
};

/** Render repo markdown (SKILL.md bodies, CONTRIBUTING.md) with GitHub-flavored extensions. */
export function Prose({ children, label }: { children: string; label?: string }) {
  return (
    <article className="prose">
      {label && <h2 className="prose-label">{label}</h2>}
      <Markdown remarkPlugins={[remarkGfm]} components={components}>
        {children}
      </Markdown>
    </article>
  );
}
