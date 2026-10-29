"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { CaretDownIcon, CaretRightIcon } from "@phosphor-icons/react";
import type { Heading } from "@/lib/markdown";

// The Details half of a skill page: a contents list built from the SKILL.md headings beside the
// rendered body. A long body starts collapsed behind "Read the full skill"; the contents list stays
// visible and opens the body before the browser jumps to the heading (the open flag is flipped on
// the DOM synchronously in the click handler, so the anchor's own navigation lands on a laid-out
// element). Deep links (#heading) and hash changes open it the same way. The body is a native
// <details>, so without JavaScript the summary still toggles it.
export function SkillDetails({
  toc,
  collapsed,
  description,
  children,
}: {
  toc: Heading[];
  collapsed: boolean;
  description: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDetailsElement>(null);
  const [open, setOpen] = useState(!collapsed);

  const reveal = () => {
    if (ref.current && !ref.current.open) {
      ref.current.open = true;
      setOpen(true);
    }
  };

  useEffect(() => {
    const openForHash = () => {
      const body = ref.current;
      if (!body) return;
      const id = decodeURIComponent(location.hash.slice(1));
      let target: Element | null = null;
      try {
        target = id ? body.querySelector(`#${CSS.escape(id)}`) : null;
      } catch {}
      if (target && !body.open) {
        body.open = true;
        requestAnimationFrame(() => target?.scrollIntoView());
      }
      // Browsers expand a <details> themselves when a fragment inside it is navigated to, and on a
      // deep link that happens before hydration; take the DOM's word so the label matches.
      setOpen(body.open);
    };
    openForHash();
    addEventListener("hashchange", openForHash);
    return () => removeEventListener("hashchange", openForHash);
  }, []);

  const sections = toc.filter((h) => h.level === 2).length;
  return (
    <section className="details" id="skill-details" aria-labelledby="details-title">
      <div className="details-head">
        <h2 id="details-title">Details</h2>
        <p>The full SKILL.md, as Claude reads it.</p>
      </div>
      <details className="desc-full">
        <summary>The description Claude uses to decide when to load this skill</summary>
        <p>{description}</p>
      </details>
      <div className="details-grid">
        {toc.length > 0 && (
          <nav className="toc toc-always" aria-label="Sections of this skill">
            {toc.map((h) => (
              <a key={h.id} href={`#${h.id}`} className={h.level > 2 ? "sub" : undefined} onClick={reveal}>
                {h.text}
              </a>
            ))}
          </nav>
        )}
        {/* suppressHydrationWarning: on a deep link the browser opens this before React hydrates (see the effect). */}
        <details
          ref={ref}
          className="skill-body"
          open={open}
          onToggle={(e) => setOpen(e.currentTarget.open)}
          suppressHydrationWarning
        >
          <summary>
            {open ? <CaretDownIcon size={14} weight="bold" aria-hidden="true" /> : <CaretRightIcon size={14} weight="bold" aria-hidden="true" />}
            {open ? "Collapse" : sections > 1 ? `Read the full skill (${sections} sections)` : "Read the full skill"}
          </summary>
          {children}
          <p className="body-foot">
            <a href="#skill-details">Back to the top of Details</a>
          </p>
        </details>
      </div>
    </section>
  );
}
