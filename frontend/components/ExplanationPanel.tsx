"use client";

import { useState } from "react";
import type { ExplanationResponse } from "@/lib/api";
import LanguageToggle, { type Language } from "./LanguageToggle";
import LegalAidRedirect from "./LegalAidRedirect";

type Level = "gist" | "clause_by_clause" | "legal_view";

/**
 * C17: explanation panel with working EN/KN and gist/clause/legal-view
 * toggles, backed by live API data (ExplanationResponse from C10).
 */
export default function ExplanationPanel({
  explanation,
}: {
  explanation: ExplanationResponse;
}) {
  const [language, setLanguage] = useState<Language>("english");
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
      <LanguageToggle value={language} onChange={setLanguage} />
      <div className="toggle-group">
        <button
          className={`toggle ${level === "gist" ? "active" : ""}`}
          onClick={() => setLevel("gist")}
          type="button"
        >
          One-line gist
        </button>
        <button
          className={`toggle ${level === "clause_by_clause" ? "active" : ""}`}
          onClick={() => setLevel("clause_by_clause")}
          type="button"
        >
          Clause-by-clause
        </button>
        <button
          className={`toggle ${level === "legal_view" ? "active" : ""}`}
          onClick={() => setLevel("legal_view")}
          type="button"
        >
          Legal view
        </button>
      </div>
      <div className="doc-text">{levelText}</div>
      {levels.citations.length > 0 && (
        <p style={{ fontSize: "0.8rem", color: "#555" }}>
          Citations: {levels.citations.join(", ")}
        </p>
      )}
      {explanation.mock && (
        <p style={{ fontSize: "0.75rem", color: "#a94442" }}>
          (offline mock mode — not a live Gemini response)
        </p>
      )}
    </div>
  );
}
