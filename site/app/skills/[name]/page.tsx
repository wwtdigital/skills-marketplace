import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowUpRightIcon, CaretRightIcon, DownloadSimpleIcon } from "@phosphor-icons/react/ssr";
import { CopyCmd } from "@/components/CopyCmd";
import { Footer } from "@/components/Footer";
import { Prose } from "@/components/Prose";
import { asset, formatDate } from "@/lib/catalog";
import { findSkill, loadCatalog } from "@/lib/load";

type Props = { params: Promise<{ name: string }> };

// Only skills in the catalog exist; anything else is a 404.
export const dynamicParams = false;

export function generateStaticParams() {
  return (loadCatalog()?.plugins ?? []).flatMap((p) => p.skills.map((s) => ({ name: s.name })));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const found = findSkill(loadCatalog(), (await params).name);
  return found ? { title: found.skill.name, description: found.skill.description } : {};
}

export default async function SkillPage({ params }: Props) {
  const catalog = loadCatalog();
  const found = findSkill(catalog, (await params).name);
  if (!found) notFound();
  const { plugin: p, skill: s } = found;
  const includes = [s.has_scripts && "scripts", s.has_references && "references"].filter(Boolean).join(", ");

  return (
    <>
      <main className="wrap doc">
        <nav className="crumbs" aria-label="Breadcrumb">
          <Link href="/#browse">Skills</Link>
          <CaretRightIcon size={12} aria-hidden="true" />
          <Link href={`/#${p.name}`}>{p.displayName}</Link>
        </nav>
        <header className="doc-head">
          <h1>{s.name}</h1>
          <div className="sub">
            <span className={`badge ${s.status}`}>{s.status}</span>
            {s.version && <span className="mono">v{s.version}</span>}
            <span>in {p.displayName}</span>
          </div>
          <p className="desc">{s.description}</p>
        </header>

        <div className="doc-grid">
          {s.body ? <Prose>{s.body}</Prose> : <div />}
          <aside className="aside" aria-label="Install and details">
            <p className="aside-label">Install the {p.displayName} bundle</p>
            <CopyCmd text={p.install} />
            <a className="btn btn-primary" href={asset(s.download)} download>
              <DownloadSimpleIcon size={16} aria-hidden="true" />
              Download .skill ({Math.max(1, Math.round(s.download_bytes / 1024))} KB)
            </a>
            <dl className="kv">
              <dt>Owner</dt>
              <dd>{s.owner ? <a href={`mailto:${s.owner}`}>{s.owner}</a> : "Not set"}</dd>
              <dt>Connectors</dt>
              <dd>
                {s.connectors.length
                  ? s.connectors.map((c) => (
                      <span key={c} className="tag">
                        {c}
                      </span>
                    ))
                  : "None"}
              </dd>
              <dt>Includes</dt>
              <dd>{includes || "SKILL.md only"}</dd>
              <dt>Updated</dt>
              <dd>{formatDate(s.updated)}</dd>
              <dt>Source</dt>
              <dd>
                <a href={s.source} target="_blank" rel="noopener">
                  GitHub <ArrowUpRightIcon size={12} weight="bold" aria-hidden="true" />
                </a>
              </dd>
            </dl>
          </aside>
        </div>
      </main>
      <Footer catalog={catalog} />
    </>
  );
}
