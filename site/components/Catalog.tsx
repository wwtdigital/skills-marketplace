"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowUpRightIcon, DownloadSimpleIcon, MagnifyingGlassIcon, PlugsConnectedIcon } from "@phosphor-icons/react";
import { asset, type McpServer, type Plugin, type Skill } from "@/lib/catalog";
import { CopyCmd } from "./CopyCmd";

const STATUSES = ["stable", "beta", "draft"] as const;
const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

function matches(s: Skill, q: string, statuses: Set<string>) {
  if (statuses.size && !statuses.has(s.status)) return false;
  if (!q) return true;
  return [s.name, s.description, s.summary, ...s.connectors].join(" ").toLowerCase().includes(q);
}

export function Catalog({ plugins }: { plugins: Plugin[] }) {
  const [query, setQuery] = useState("");
  const [statuses, setStatuses] = useState<Set<string>>(new Set());
  const q = query.trim().toLowerCase();
  const filtering = Boolean(q || statuses.size);

  const toggleStatus = (s: string) =>
    setStatuses((prev) => {
      const next = new Set(prev);
      if (next.has(s)) next.delete(s);
      else next.add(s);
      return next;
    });

  const rows = plugins.map((p) => ({
    plugin: p,
    skills: p.skills.filter((s) => matches(s, q, statuses)),
    servers: statuses.size ? [] : p.mcp_servers.filter((m) => !q || m.name.includes(q) || (m.url ?? "").includes(q)),
  }));
  const populated = rows.filter(({ plugin: p, skills, servers }) =>
    filtering ? skills.length || servers.length : p.skills.length || p.mcp_servers.length,
  );
  const empty = filtering ? [] : rows.filter(({ plugin: p }) => !p.skills.length && !p.mcp_servers.length);
  const nSkills = plugins.reduce((n, p) => n + p.skills.length, 0);
  const nServers = plugins.reduce((n, p) => n + p.mcp_servers.length, 0);

  return (
    <section className="catalog" id="browse" aria-labelledby="browse-title">
      <div className="wrap">
        <div className="catalog-head">
          <div>
            <h2 id="browse-title">Skills by category</h2>
            <p className="counts">
              {plural(plugins.length, "plugin")}, {plural(nSkills, "skill")} and {plural(nServers, "MCP server")}.
            </p>
          </div>
          <div className="toolbar">
            <label className="search">
              <span className="visually-hidden">Search skills</span>
              <MagnifyingGlassIcon size={16} aria-hidden="true" />
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search, e.g. status report or brand"
              />
            </label>
            <div className="chips" role="group" aria-label="Filter by status">
              {STATUSES.map((s) => (
                <button key={s} className="chip" aria-pressed={statuses.has(s)} onClick={() => toggleStatus(s)}>
                  {s[0].toUpperCase() + s.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {populated.length === 0 && (
          <div className="empty">
            Nothing matches that. Try another word, or <Link href="/contribute">contribute</Link> the skill you were
            looking for.
          </div>
        )}

        {populated.map(({ plugin: p, skills, servers }) => (
          <article key={p.name} className="category" id={p.name} aria-labelledby={`${p.name}-title`}>
            <div className="category-meta">
              {p.category && p.category !== p.name && (
                <p className="addon">
                  {plugins.find((c) => c.name === p.category)?.displayName ?? p.category} add-on, installed separately
                </p>
              )}
              <h3 id={`${p.name}-title`}>{p.displayName}</h3>
              <p>{p.description}</p>
              <div className="facts">
                <span>
                  <b>{p.skills.length}</b> {p.skills.length === 1 ? "skill" : "skills"}
                </span>
                {p.mcp_servers.length > 0 && (
                  <span>
                    <b>{p.mcp_servers.length}</b> MCP
                  </span>
                )}
                {p.version && <span className="mono">v{p.version}</span>}
              </div>
              <CopyCmd text={p.install} />
              <div className="links">
                <a className="btn btn-sm btn-quiet" href={asset(p.download)} download>
                  <DownloadSimpleIcon size={15} aria-hidden="true" /> Bundle .zip
                </a>
                <a className="btn btn-sm btn-quiet" href={p.source} target="_blank" rel="noopener">
                  Source <ArrowUpRightIcon size={13} weight="bold" aria-hidden="true" />
                </a>
              </div>
            </div>
            <div className="category-body">
              {servers.length > 0 && <McpBlock servers={servers} />}
              {skills.length > 0 && (
                <div className="skills">
                  {skills.map((s) => (
                    <SkillCard key={s.name} skill={s} />
                  ))}
                </div>
              )}
              {!p.skills.length && !filtering && (
                <p className="muted" style={{ margin: 0, fontSize: 14.5 }}>
                  No skills in this bundle yet. <Link href="/contribute">Contribute</Link> one.
                </p>
              )}
            </div>
          </article>
        ))}

        {empty.length > 0 && (
          <div className="empty-row">
            <span>Waiting for their first skill:</span>
            <span className="names">
              {empty.map(({ plugin: p }) => (
                <span key={p.name} id={p.name} title={p.description}>
                  {p.displayName}
                </span>
              ))}
            </span>
            <Link href="/contribute">Contribute</Link>
          </div>
        )}
      </div>
    </section>
  );
}

function McpBlock({ servers }: { servers: McpServer[] }) {
  return (
    <div className="mcp">
      <PlugsConnectedIcon size={22} aria-hidden="true" />
      <div>
        <h4>{servers.length === 1 ? "Includes an MCP server" : "Includes MCP servers"}</h4>
        <p>
          Connected when you install this plugin. If it asks you to sign in, run <code>/mcp</code>.
        </p>
        <ul>
          {servers.map((m) => (
            <li key={m.name}>
              <code>{m.name}</code>
              {m.url && <span className="mono">{new URL(m.url).host}</span>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function SkillCard({ skill: s }: { skill: Skill }) {
  return (
    <article className="skill">
      <div className="top">
        <h4>
          <Link href={`/skills/${s.name}`}>{s.name}</Link>
        </h4>
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
        <a className="btn btn-sm" href={asset(s.download)} download aria-label={`Download ${s.name}.skill`}>
          <DownloadSimpleIcon size={15} aria-hidden="true" /> .skill
        </a>
      </div>
    </article>
  );
}
