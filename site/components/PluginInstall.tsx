"use client";

import type { Plugin } from "@/lib/catalog";
import { CopyCmd } from "./CopyCmd";
import { useInstallMode } from "./InstallMode";

// The install line for one plugin. Claude Code, URL and admin visitors get the command to copy.
// Cowork / Desktop visitors have no command to paste (the app has no slash command for this), so
// they get the click path instead, as plain text with no copy button: what shows is what there is.
export function PluginInstall({ plugin }: { plugin: Plugin }) {
  const { mode } = useInstallMode();
  if (mode !== "cowork") return <CopyCmd text={plugin.install} />;
  return (
    <p className="install-note">
      In Cowork: <b>Customize</b> &gt; <b>Plugins</b> &gt; <b>Discover</b> &gt; <b>{plugin.displayName}</b> &gt;{" "}
      <b>Add</b>
    </p>
  );
}
