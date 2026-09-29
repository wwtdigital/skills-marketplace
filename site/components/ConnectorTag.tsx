import { PlugIcon } from "@phosphor-icons/react/ssr";
import { asset, connectorName, isBundled, type Plugin } from "@/lib/catalog";
import ICONS from "@/lib/connector-icons.json";

// Each service's own logo, saved into public/connectors/ by scripts/fetch-connector-icons.ts.
// Anything without one (including our own MCP servers) gets a plain plug.
const FILES: Record<string, string> = ICONS;

export function ConnectorIcon({ name, size = 13 }: { name: string; size?: number }) {
  const file = FILES[name];
  if (!file) return <PlugIcon size={size} aria-hidden="true" />;
  return <img className="logo" src={asset(`connectors/${file}`)} width={size} height={size} alt="" />;
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
