"use client";

import { useState } from "react";
import { CheckIcon, CopyIcon } from "@phosphor-icons/react";

export function CopyCmd({ text, className = "" }: { text: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  const multiline = text.includes("\n");
  return (
    <div className={`cmd ${multiline ? "cmd-multiline" : ""} ${className}`}>
      <code>{text}</code>
      <button
        type="button"
        className="copy"
        data-copied={copied}
        aria-label={copied ? "Copied" : "Copy command"}
        title="Copy"
        onClick={() =>
          navigator.clipboard?.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 1400);
          })
        }
      >
        {copied ? <CheckIcon size={15} weight="bold" /> : <CopyIcon size={15} />}
      </button>
      <span className="visually-hidden" aria-live="polite">
        {copied ? "Copied to clipboard" : ""}
      </span>
    </div>
  );
}
