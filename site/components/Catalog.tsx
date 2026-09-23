"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { asset, type Plugin, type Skill } from "@/lib/catalog";
import { CopyCmd } from "./CopyCmd";

const STATUSES = ["stable", "beta", "draft"] as const;

function matches(s: Skill, q: string, statuses: Set<string>) {
  if (statuses.size && !statuses.has(s.status)) return false;
  if (!q) return true;
  return [s.name, s.description, s.summary, ...s.connectors].join(" ").toLowerCase().includes(q);
}

export function Catalog({ plugins, repo }: { plugins: Plugin[]; repo: string }) {
  const [query, setQuery] = useState("");
  const [statuses, setStatuses] = useState<Set<string>>(new Set());
  const [open, setOpen] = useState<Set<string>>(new Set());

  // Plugin manifests link to /#<plugin>; open that bundle on arrival.
  useEffect(() => {
    const openFromHash = () => {
      const id = decodeURIComponent(location.hash.slice(1));
      if (id) setOpen((prev) => new Set(prev).add(id));
    };
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
    return () => window.removeEventListener("hashchange", openFromHash);
  }, []);

  const q = query.trim().toLowerCase();
  const filtering = Boolean(q || statuses.size);

  const toggleStatus = (s: string) =>
    setStatuses((prev) => {
      const next = new Set(prev);
      next.has(s) ? next.delete(s) : next.add(s);
      return next;
    });

  const visible = plugins
    .map((p) => ({ plugin: p, skills: p.skills.filter((s) => matches(s, q, statuses)) }))
    .filter(({ skills }) => !filtering || skills.length);

  return (
    <section id="browse">
      <div className="toolbar">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search skills — e.g. status report, staffing, review"
          aria-label="Search skills"
        />
        <div className="chips">
          {STATUSES.map((s) => (
            <button key={s} className="chip" aria-pressed={statuses.has(s)} onClick={() => toggleStatus(s)}>
              {s[0].toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {visible.length === 0 && <div className="empty">No skills match.</div>}
      {visible.map(({ plugin: p, skills }) => (
        <details
          key={p.name}
          className="plugin"
          id={p.name}
          open={filtering || open.has(p.name)}
          onToggle={(e) => {
            if (filtering) return;
            const isOpen = e.currentTarget.open;
            setOpen((prev) => {
              const next = new Set(prev);
              isOpen ? next.add(p.name) : next.delete(p.name);
              return next;
            });
          }}
        >
          <summary>
            <h2>{p.displayName}</h2>
            <div className="meta">
              <span className="count">
                {skills.length} skill{skills.length === 1 ? "" : "s"}
              </span>
              {p.version && <span className="mono">v{p.version}</span>}
              {p.author && <span>· {p.author}</span>}
            </div>
            <p className="desc">{p.description}</p>
          </summary>
          <div className="pbody">
            <div className="cmdrow">
              <CopyCmd text={p.install} />
              <a className="btn" href={asset(p.download)} download>
                Download bundle (.zip)
              </a>
              <a className="btn" href={p.source} target="_blank" rel="noopener">
                Source
              </a>
            </div>
            {skills.length ? (
              <div className="skills">
                {skills.map((s) => (
                  <SkillCard key={s.name} skill={s} />
                ))}
              </div>
            ) : (
              <div className="empty">
                No skills in this bundle yet — <a href={`${repo}/blob/main/CONTRIBUTING.md`}>be the first to add one</a>.
              </div>
            )}
          </div>
        </details>
      ))}
    </section>
  );
}

function SkillCard({ skill: s }: { skill: Skill }) {
  return (
    <article className="skill">
      <div className="top">
        <h3>
          <Link href={`/skills/${s.name}`}>{s.name}</Link>
        </h3>
        <span className={`badge ${s.status}`}>{s.status}</span>
      </div>
      <p>{s.description}</p>
      <div className="foot">
        {s.version && <span className="mono">v{s.version}</span>}
        {s.connectors.map((c) => (
          <span key={c} className="tag">
            {c}
          </span>
        ))}
        <span className="acts">
          <Link className="btn" href={`/skills/${s.name}`}>
            Details
          </Link>
          <a className="btn primary" href={asset(s.download)} download>
            Download .skill
          </a>
        </span>
      </div>
    </article>
  );
}
