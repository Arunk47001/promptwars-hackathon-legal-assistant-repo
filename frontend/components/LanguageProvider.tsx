"use client";

import { createContext, useContext, useMemo, useState } from "react";
import type { Language } from "./LanguageToggle";

/**
 * Site-wide language preference (English / Kannada). This only controls
 * which language of an already-fetched explanation is displayed — it does
 * not translate the UI chrome and it does not change any API call shape.
 * Lifted to a context so the top nav's language toggle (per the design)
 * and any per-document explanation view stay in sync, instead of each
 * having their own disconnected local toggle.
 */
interface LanguageContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextValue>({
  language: "english",
  setLanguage: () => {},
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>("english");
  const value = useMemo(() => ({ language, setLanguage }), [language]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  return useContext(LanguageContext);
}
