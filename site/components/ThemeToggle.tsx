"use client";

import { MoonIcon, SunIcon } from "@phosphor-icons/react";
import { THEME_KEY } from "@/lib/theme";

// Both icons render; CSS shows the one matching the current theme, so there's no hydration mismatch.
export function ThemeToggle() {
  function toggle() {
    const root = document.documentElement;
    const current = root.dataset.theme ?? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch {}
  }
  return (
    <button type="button" className="theme-toggle" onClick={toggle} aria-label="Toggle light or dark mode" title="Toggle theme">
      <SunIcon className="icon-sun" size={17} aria-hidden="true" />
      <MoonIcon className="icon-moon" size={17} aria-hidden="true" />
    </button>
  );
}
