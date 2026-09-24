"use client";

/**
 * C2/C17: EN/KN language-toggle stub, later wired live in C17.
 * Rendered in the top nav (site-wide preference) and reused anywhere an
 * explanation's displayed language needs to be switched.
 */
export type Language = "english" | "kannada";

export default function LanguageToggle({
  value,
  onChange,
}: {
  value: Language;
  onChange: (lang: Language) => void;
}) {
  return (
    <div className="lang-toggle" role="group" aria-label="Language">
      <button
        className={`lang-toggle-btn ${value === "english" ? "active" : ""}`}
        onClick={() => onChange("english")}
        type="button"
      >
        English
      </button>
      <button
        className={`lang-toggle-btn font-kannada ${value === "kannada" ? "active" : ""}`}
        onClick={() => onChange("kannada")}
        type="button"
      >
        ಕನ್ನಡ
      </button>
    </div>
  );
}
