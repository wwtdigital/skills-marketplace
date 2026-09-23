"use client";

import { useState } from "react";

export function CopyCmd({ text, className = "" }: { text: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <pre className={`cmd ${className}`}>
      <code>{text}</code>
      <button
        type="button"
        onClick={() =>
          navigator.clipboard?.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 1200);
          })
        }
      >
        {copied ? "Copied" : "Copy"}
      </button>
    </pre>
  );
}
