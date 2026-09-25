import type { Icon } from "@phosphor-icons/react";
import {
  FigmaLogoIcon,
  GithubLogoIcon,
  GoogleDriveLogoIcon,
  MicrosoftExcelLogoIcon,
  MicrosoftOutlookLogoIcon,
  MicrosoftPowerpointLogoIcon,
  MicrosoftTeamsLogoIcon,
  MicrosoftWordLogoIcon,
  NotionLogoIcon,
  PlugIcon,
  SlackLogoIcon,
} from "@phosphor-icons/react/ssr";
import { connectorName, isBundled, type Plugin } from "@/lib/catalog";

// Monochrome logos so tags stay in the site's one-accent palette. Anything not listed
// (including our own MCP servers) gets a plain plug.
const ICONS: Record<string, Icon> = {
  notion: NotionLogoIcon, figma: FigmaLogoIcon, slack: SlackLogoIcon, github: GithubLogoIcon,
  "google-drive": GoogleDriveLogoIcon, outlook: MicrosoftOutlookLogoIcon, teams: MicrosoftTeamsLogoIcon,
  "microsoft-teams": MicrosoftTeamsLogoIcon, excel: MicrosoftExcelLogoIcon, word: MicrosoftWordLogoIcon,
  powerpoint: MicrosoftPowerpointLogoIcon,
};

export function ConnectorIcon({ name, size = 13 }: { name: string; size?: number }) {
  const I = ICONS[name] ?? PlugIcon;
  return <I size={size} weight={ICONS[name] ? "fill" : "regular"} aria-hidden="true" />;
}

export function ConnectorTag({ plugin, connector: c }: { plugin: Plugin; connector: string }) {
  const label = isBundled(plugin, c)
    ? `${connectorName(c)} included: connects when you install the plugin`
    : `Needs ${connectorName(c)}: connect it in the Claude app first`;
  return (
    <span className="tag tag-icon" role="img" aria-label={label} title={label}>
      <ConnectorIcon name={c} size={14} />
    </span>
  );
}
