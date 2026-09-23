"use client";

/**
 * C2/C17: EN/KN language-toggle stub, later wired live in C17.
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
    <div className="toggle-group" role="group" aria-label="Language">
      <button
        className={`toggle ${value === "english" ? "active" : ""}`}
        onClick={() => onChange("english")}
        type="button"
      >
        EN
      </button>
      <button
        className={`toggle ${value === "kannada" ? "active" : ""}`}
        onClick={() => onChange("kannada")}
        type="button"
      >
        ಕನ್ನಡ
      </button>
    </div>
  );
}
