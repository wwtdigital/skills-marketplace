"use client";

import { useState } from "react";
import { CopyCmd } from "./CopyCmd";

const TABS = [
  { id: "code", label: "Claude Code" },
  { id: "cowork", label: "Cowork / Desktop" },
  { id: "nogit", label: "No GitHub account" },
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
      enabledPlugins: { [`brand-and-voice@${marketplace}`]: true },
    },
    null,
    2,
  );

  return (
    <section className="install" id="install">
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
              Add the marketplace once:
              <CopyCmd text={`/plugin marketplace add ${slug}`} />
            </li>
            <li>
              Install the bundle(s) you want, e.g.
              <CopyCmd text={`/plugin install creative-tech@${marketplace}`} />
            </li>
            <li>
              Later, pull new skills with
              <CopyCmd text={`/plugin marketplace update ${marketplace}`} />
              or turn on auto-update once in <b>/plugin → Marketplaces</b> (it&apos;s off by default for
              non-Anthropic marketplaces).
            </li>
          </ol>
        </div>
      )}
      {tab === "cowork" && (
        <div className="panel" role="tabpanel">
          <ol>
            <li>
              In the Claude desktop app open <b>Customize → Plugins</b>.
            </li>
            <li>
              Choose <b>Add marketplace</b> and paste:
              <CopyCmd text={repo} />
            </li>
            <li>
              Pick the discipline bundles you want and click <b>Install</b>. Skills appear in Claude&apos;s skill
              list immediately.
            </li>
          </ol>
        </div>
      )}
      {tab === "nogit" && (
        <div className="panel" role="tabpanel">
          {marketplaceUrl && (
            <>
              <p className="panel-lead">
                <b>Claude Code:</b> add the marketplace straight from this site. No GitHub account needed, and you
                still get updates:
              </p>
              <ol>
                <li>
                  <CopyCmd text={`/plugin marketplace add ${marketplaceUrl}`} />
                </li>
                <li>
                  <CopyCmd text={`/plugin install creative-tech@${marketplace}`} />
                </li>
              </ol>
              <p className="panel-lead">Or install a single skill by hand:</p>
            </>
          )}
          <ol>
            <li>
              Find a skill below and click <b>Download .skill</b>.
            </li>
            <li>
              <b>Cowork:</b> open <b>Customize → Skills</b> and add the file (or drop it into the chat and choose{" "}
              <i>Save skill</i>).
            </li>
            <li>
              <b>Claude Code:</b> unzip it into <code>~/.claude/skills/</code> — the folder name is the skill name.
            </li>
            <li>Updates aren&apos;t automatic this way; check back here or ask your discipline owner.</li>
          </ol>
        </div>
      )}
      {tab === "admin" && (
        <div className="panel" role="tabpanel">
          <ol>
            <li>
              Pre-register the marketplace for everyone via managed settings:
              <CopyCmd text={managed} />
            </li>
            <li>
              Add <code>{marketplace}</code> to <code>strictKnownMarketplaces</code> if you restrict which marketplaces
              users may add.
            </li>
            <li>
              Validate the repo locally with <code>claude plugin validate .</code> — CI runs it on every PR.
            </li>
          </ol>
        </div>
      )}
    </section>
  );
}
