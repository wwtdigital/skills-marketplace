"use client";

import { CopyCmd } from "./CopyCmd";
import { useInstallMode } from "./InstallMode";

const TABS = [
  { id: "code", label: "Claude Code" },
  { id: "github", label: "GitHub (org members)" },
  { id: "cowork", label: "Cowork / Desktop" },
  { id: "admin", label: "Admins" },
] as const;

// The marketplace source Claude Code reads from this site, with the team access key as a bearer
// header. Claude Code sends the header on marketplace.json and on every plugin zip it downloads from
// the same origin, so one entry covers installs and updates. (Needs Claude Code 2.1.286 or later.)
function urlSource(marketplaceUrl: string, token: string | null) {
  return {
    source: "url",
    url: marketplaceUrl,
    headers: { Authorization: `Bearer ${token ?? "<team access key from Slack>"}` },
  };
}

export function InstallTabs({
  repo,
  marketplace,
  marketplaceUrl,
  accessToken,
}: {
  repo: string;
  marketplace: string;
  marketplaceUrl: string | null;
  accessToken: string | null;
}) {
  const { mode: tab, setMode: setTab } = useInstallMode();
  const slug = repo.replace(/^https:\/\/github\.com\//, "");
  const url = marketplaceUrl ?? "https://skills-marketplace.wwtdigital.io/marketplace.json";
  const userSettings = JSON.stringify(
    { extraKnownMarketplaces: { [marketplace]: { source: urlSource(url, accessToken), autoUpdate: true } } },
    null,
    2,
  );
  const managed = JSON.stringify(
    {
      // Third-party marketplaces don't auto-update by default; autoUpdate turns it on org-wide.
      extraKnownMarketplaces: { [marketplace]: { source: urlSource(url, accessToken), autoUpdate: true } },
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
              Add this to <code>~/.claude/settings.json</code> (merge it in if the file already has{" "}
              <code>extraKnownMarketplaces</code>). It carries the team access key, so there&apos;s nothing else to
              sign in to:
              <CopyCmd text={userSettings} />
            </li>
            <li>
              Start a new Claude Code session, then install the bundles you want:
              <CopyCmd text={`/plugin install presentation@${marketplace}`} />
            </li>
            <li>
              New skills arrive on their own (<code>autoUpdate</code>), or pull them now with{" "}
              <code>/plugin marketplace update {marketplace}</code>.
            </li>
          </ol>
          <p className="lead" style={{ marginTop: 18 }}>
            Added <code>{marketplace}</code> from GitHub before? Run <code>/plugin marketplace remove {marketplace}</code>{" "}
            first (it also removes its plugins; reinstall them after step 2). <code>/plugin marketplace add</code>{" "}
            with this site&apos;s URL doesn&apos;t work on its own because it can&apos;t send the key.
          </p>
        </div>
      )}
      {tab === "github" && (
        <div className="panel" role="tabpanel">
          <p className="lead">
            The repo is private. If you&apos;re in the WWTDigital GitHub org and git on your machine is signed in (
            <code>gh auth login</code> then <code>gh auth setup-git</code>, or an SSH key), the GitHub route works
            as before:
          </p>
          <ol>
            <li>
              <CopyCmd text={`/plugin marketplace add ${slug}`} />
            </li>
            <li>
              <CopyCmd text={`/plugin install presentation@${marketplace}`} />
            </li>
            <li>
              Pull new skills later with <code>/plugin marketplace update {marketplace}</code>, or turn on
              auto-update in <b>/plugin</b>, then <b>Marketplaces</b>.
            </li>
          </ol>
          <p className="lead" style={{ marginTop: 18 }}>
            One marketplace, one source: if you also add the Claude Code tab&apos;s entry, remove this one first.
          </p>
        </div>
      )}
      {tab === "cowork" && (
        <div className="panel" role="tabpanel">
          <p className="lead">
            <b>Customize</b> &gt; <b>Plugins</b> &gt; <b>+ Add</b> &gt; <b>Add marketplace</b>, then paste:
          </p>
          <ol>
            <li>
              <CopyCmd text={slug} />
            </li>
            <li>
              The bundles show up in your Plugins list. Enable the ones you want; their skills are available right
              away.
            </li>
          </ol>
          <p className="lead" style={{ marginTop: 18 }}>
            That dialog only takes a GitHub repo, and the repo is private, so it needs a GitHub account in the
            WWTDigital org (ask the maintainer to add you). No GitHub account? Download a bundle&apos;s <b>.zip</b>{" "}
            below, then <b>Customize</b> &gt; <b>Plugins</b> &gt; <b>+ Add</b> &gt; <b>Upload plugin</b> and pick the
            file. Single skills: download the <b>.skill</b> and use <b>Customize</b> &gt; <b>Skills</b> &gt;{" "}
            <b>+ Add</b> &gt; <b>Upload skill</b>.
          </p>
        </div>
      )}
      {tab === "admin" && (
        <div className="panel" role="tabpanel">
          <ol>
            <li>
              Register the marketplace for everyone in managed settings. The key is a team secret; managed settings
              are the right place for it:
              <CopyCmd text={managed} />
            </li>
            <li>
              If you restrict which marketplaces people can add, include the same <code>url</code> source in{" "}
              <code>strictKnownMarketplaces</code>.
            </li>
          </ol>
        </div>
      )}
    </section>
  );
}
