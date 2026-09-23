"use client";

import { useState } from "react";
import { CopyCmd } from "./CopyCmd";

const TABS = [
  { id: "code", label: "Claude Code" },
  { id: "nogit", label: "No GitHub account" },
  { id: "cowork", label: "Cowork / Desktop" },
  { id: "admin", label: "Admins" },
] as const;

export function InstallTabs({
  repo,
  marketplace,
  marketplaceUrl,
}: {
  repo: string;
  marketplace: string;
  marketplaceUrl: string | null;
}) {
  const [tab, setTab] = useState<(typeof TABS)[number]["id"]>("code");
  const slug = repo.replace(/^https:\/\/github\.com\//, "");
  const managed = JSON.stringify(
    {
      // Third-party marketplaces don't auto-update by default; autoUpdate turns it on org-wide.
      extraKnownMarketplaces: { [marketplace]: { source: { source: "github", repo: slug }, autoUpdate: true } },
      enabledPlugins: { [`presentation@${marketplace}`]: true },
    },
    null,
    2,
  );

  return (
    <section className="install rise" style={{ "--i": 3 } as React.CSSProperties} id="install" aria-label="Install">
      <div className="tabs" role="tablist">
        {TABS.map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>
      {tab === "code" && (
        <div className="panel" role="tabpanel">
          <ol>
            <li>
              Add the marketplace once (needs access to the GitHub repo):
              <CopyCmd text={`/plugin marketplace add ${slug}`} />
            </li>
            <li>
              Install the bundles you want:
              <CopyCmd text={`/plugin install presentation@${marketplace}`} />
            </li>
            <li>
              Pull new skills later with <code>/plugin marketplace update {marketplace}</code>, or turn on
              auto-update in <b>/plugin</b>, then <b>Marketplaces</b>.
            </li>
          </ol>
        </div>
      )}
      {tab === "nogit" && (
        <div className="panel" role="tabpanel">
          {marketplaceUrl && (
            <>
              <p className="lead">In Claude Code, add the marketplace from this site. Updates still work.</p>
              <ol>
                <li>
                  <CopyCmd text={`/plugin marketplace add ${marketplaceUrl}`} />
                </li>
                <li>
                  <CopyCmd text={`/plugin install presentation@${marketplace}`} />
                </li>
              </ol>
              <p className="lead" style={{ marginTop: 18 }}>
                Or install one skill by hand: download its <b>.skill</b> file below, then add it in Cowork under{" "}
                <b>Customize</b> &gt; <b>Skills</b> &gt; <b>+ Add</b> &gt; <b>Upload skill</b>, or unzip it into{" "}
                <code>~/.claude/skills/</code>.
              </p>
            </>
          )}
        </div>
      )}
      {tab === "cowork" && (
        <div className="panel" role="tabpanel">
          <p className="lead">
            In the Claude desktop app: <b>Customize</b> &gt; <b>Plugins</b> &gt; <b>+ Add</b> &gt;{" "}
            <b>Add marketplace</b>. Paste whichever it asks for:
          </p>
          <ol>
            <li>
              GitHub repo:
              <CopyCmd text={slug} />
            </li>
            <li>
              or Marketplace URL (no GitHub account needed):
              {marketplaceUrl && <CopyCmd text={marketplaceUrl} />}
            </li>
            <li>
              The bundles show up in your Plugins list. Enable the ones you want; their skills are available right
              away.
            </li>
          </ol>
          <p className="lead" style={{ marginTop: 18 }}>
            No marketplace at all: download a bundle&apos;s <b>.zip</b> below, then <b>Customize</b> &gt;{" "}
            <b>Plugins</b> &gt; <b>+ Add</b> &gt; <b>Upload plugin</b> and pick the file.
          </p>
        </div>
      )}
      {tab === "admin" && (
        <div className="panel" role="tabpanel">
          <ol>
            <li>
              Register the marketplace for everyone in managed settings:
              <CopyCmd text={managed} />
            </li>
            <li>
              If you restrict which marketplaces people can add, include <code>{marketplace}</code> in{" "}
              <code>strictKnownMarketplaces</code>.
            </li>
          </ol>
        </div>
      )}
    </section>
  );
}
