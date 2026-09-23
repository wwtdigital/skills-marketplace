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
                <b>Customize</b>, <b>Skills</b>, or unzip it into <code>~/.claude/skills/</code>.
              </p>
            </>
          )}
        </div>
      )}
      {tab === "cowork" && (
        <div className="panel" role="tabpanel">
          <ol>
            <li>
              In the Claude desktop app, open <b>Customize</b>, then <b>Plugins</b>.
            </li>
            <li>
              Choose <b>Add marketplace</b> and paste:
              <CopyCmd text={repo} />
            </li>
            <li>
              Pick the bundles you want and click <b>Install</b>. The skills show up in Claude&apos;s skill list
              straight away.
            </li>
          </ol>
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
