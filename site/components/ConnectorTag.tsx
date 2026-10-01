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

// The tag shows only the logo, so the words live in visually-hidden text: screen readers read it and
// a plain-text copy of the card keeps it ("Needs Notion"), where an icon alone would vanish. The
// trailing space keeps neighbouring tags from running together. `title` is the hover explanation.
export function ConnectorTag({ plugin, connector: c }: { plugin: Plugin; connector: string }) {
  const name = connectorName(c);
  const bundled = isBundled(plugin, c);
  const words = bundled ? `${name} included` : `Needs ${name}`;
  const hover = bundled
    ? `${name} included: connects when you install the plugin`
    : `Needs ${name}: connect it in the Claude app first`;
  return (
    <span className="tag tag-icon" title={hover}>
      <ConnectorIcon name={c} size={14} />
      <span className="visually-hidden">{words} </span>
    </span>
  );
}
