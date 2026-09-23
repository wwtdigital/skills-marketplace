import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CopyCmd } from "@/components/CopyCmd";
import { Footer } from "@/components/Footer";
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
      <main className="wrap detail">
        <p className="crumbs">
          <Link href="/#browse">Skills</Link> / <Link href={`/#${p.name}`}>{p.displayName}</Link>
        </p>
        <h1>{s.name}</h1>
        <div className="sub">
          <span className={`badge ${s.status}`}>{s.status}</span>
          <span>
            in <b>{p.displayName}</b>
          </span>
          {s.version && <span className="mono">v{s.version}</span>}
        </div>
        <div className="full">{s.description}</div>

        <dl className="kv">
          <dt>Owner</dt>
          <dd>{s.owner ? <a href={`mailto:${s.owner}`}>{s.owner}</a> : "—"}</dd>
          <dt>Connectors</dt>
          <dd>
            {s.connectors.length
              ? s.connectors.map((c) => (
                  <span key={c} className="tag">
                    {c}
                  </span>
                ))
              : "none"}
          </dd>
          <dt>Includes</dt>
          <dd>{includes || "SKILL.md only"}</dd>
          <dt>Updated</dt>
          <dd>{formatDate(s.updated)}</dd>
          <dt>Install bundle</dt>
          <dd>
            <CopyCmd text={p.install} className="inline" />
          </dd>
        </dl>

        <div className="row">
          <a className="btn primary" href={asset(s.download)} download>
            Download .skill ({Math.max(1, Math.round(s.download_bytes / 1024))} KB)
          </a>
          <a className="btn" href={s.source} target="_blank" rel="noopener">
            View source
          </a>
        </div>

        {s.body && (
          <article className="prose">
            <h2 className="prose-label">SKILL.md</h2>
            <Markdown remarkPlugins={[remarkGfm]}>{s.body}</Markdown>
          </article>
        )}
      </main>
      <Footer catalog={catalog} />
    </>
  );
}
