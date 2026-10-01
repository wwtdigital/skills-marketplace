"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

// Which install tab the visitor picked. The install tabs set it, and every plugin card and skill
// page reads it, so a Cowork visitor sees where to click in Customize instead of a CLI command.
// Remembered in the browser; the server render always starts on "code" so nothing mismatches.
export const INSTALL_MODES = ["code", "nogit", "cowork", "admin"] as const;
export type InstallMode = (typeof INSTALL_MODES)[number];

const KEY = "install-mode";
const Ctx = createContext<{ mode: InstallMode; setMode: (m: InstallMode) => void }>({ mode: "code", setMode: () => {} });

export function InstallModeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<InstallMode>("code");
  useEffect(() => {
    try {
      const saved = localStorage.getItem(KEY) as InstallMode | null;
      if (saved && INSTALL_MODES.includes(saved)) setModeState(saved);
    } catch {}
  }, []);
  const setMode = useCallback((m: InstallMode) => {
    setModeState(m);
    try {
      localStorage.setItem(KEY, m);
    } catch {}
  }, []);
  return <Ctx.Provider value={{ mode, setMode }}>{children}</Ctx.Provider>;
}

export const useInstallMode = () => useContext(Ctx);
