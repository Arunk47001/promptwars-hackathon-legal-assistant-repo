"use client";

import { useState } from "react";
import type { ExplanationResponse } from "@/lib/api";
import { useLanguage } from "./LanguageProvider";
import LegalAidRedirect from "./LegalAidRedirect";

type Level = "gist" | "clause_by_clause" | "legal_view";

const LEVEL_LABELS: Record<Level, string> = {
  gist: "One-line gist",
  clause_by_clause: "Clause-by-clause",
  legal_view: "Legal view",
};

/**
 * C17: explanation panel with working EN/KN and gist/clause/legal-view
 * toggles, backed by live API data (ExplanationResponse from C10). The
 * language toggle itself now lives in the top nav (a site-wide preference,
 * see LanguageProvider) so switching it there updates any open explanation
 * in place.
 */
export default function ExplanationPanel({
  explanation,
}: {
  explanation: ExplanationResponse;
}) {
  const { language } = useLanguage();
  const [level, setLevel] = useState<Level>("gist");

  if (explanation.guardrail.high_stakes) {
    return (
      <LegalAidRedirect
        message={
          explanation.guardrail.legal_aid_redirect ||
          "This document may involve a high-stakes situation. Please consult a lawyer."
        }
      />
    );
  }

  const levels = explanation[language];
  const levelText = levels[level];

  return (
    <div>
      <h2>Explanation</h2>
      <div className="toggle-group">
        {(Object.keys(LEVEL_LABELS) as Level[]).map((l) => (
          <button
            key={l}
            className={`toggle ${level === l ? "active" : ""}`}
            onClick={() => setLevel(l)}
            type="button"
          >
            {LEVEL_LABELS[l]}
          </button>
        ))}
      </div>
      <div className="doc-text">{levelText}</div>
      {levels.citations.length > 0 && (
        <p className="citation-text">Citations: {levels.citations.join(", ")}</p>
      )}
      {explanation.mock && (
        <p className="mock-note">(offline mock mode — not a live Gemini response)</p>
      )}
    </div>
  );
}
