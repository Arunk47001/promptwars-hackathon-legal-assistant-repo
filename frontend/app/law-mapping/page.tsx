"use client";

import { useState } from "react";
import { api, type LawMappingResponse } from "@/lib/api";
import DisclaimerBanner from "@/components/DisclaimerBanner";

const CODE_OPTIONS = [
  { value: "", label: "Any code" },
  { value: "IPC", label: "IPC" },
  { value: "CrPC", label: "CrPC" },
  { value: "Evidence Act", label: "Evidence Act" },
  { value: "BNS", label: "BNS" },
  { value: "BNSS", label: "BNSS" },
  { value: "BSA", label: "BSA" },
];

/**
 * C21: standalone law-mapping lookup page calling C14, independent of any
 * uploaded document.
 */
export default function LawMappingPage() {
  const [section, setSection] = useState("");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<LawMappingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLookup() {
    if (!section.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.lookupLawMapping(section.trim(), code || undefined);
      setResult(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lookup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <DisclaimerBanner />
      <div className="page-shell page-shell-narrow">
        <h1 className="page-heading">Old section &rarr; new section</h1>
        <p className="page-sub">
          Find the new BNS, BNSS or BSA number for an IPC, CrPC or Evidence
          Act section, or the other way round.
        </p>
        <div className="law-mapping-search">
          <input
            className="mono-input"
            placeholder="Section number, e.g. 420 or 103"
            value={section}
            onChange={(e) => setSection(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLookup()}
          />
          <select
            className="mono-input"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            aria-label="Code"
          >
            {CODE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <button className="primary" onClick={handleLookup} disabled={loading}>
            {loading ? "Looking up..." : "Look up"}
          </button>
        </div>
        {error && <p className="error-text">{error}</p>}

        {result && (
          <div className="law-mapping-results">
            {result.results.length === 0 ? (
              <p>No mapping found for &quot;{result.query}&quot;.</p>
            ) : (
              result.results.map((m, i) => (
                <div className="law-mapping-row" key={i}>
                  <span className="mono-label old-section">
                    {m.old_code} {m.old_section}
                  </span>
                  <span className="law-mapping-arrow" aria-hidden="true">
                    &rarr;
                  </span>
                  <span className="mono-label new-section">
                    {m.new_code} {m.new_section}
                  </span>
                  <span className="law-mapping-description">{m.description}</span>
                </div>
              ))
            )}
          </div>
        )}

        <p className="page-footnote">
          BNS, BNSS and BSA replaced the IPC, CrPC and Evidence Act from 1 July
          2024. Offences before that date are still tried under the old
          codes.
        </p>
      </div>
    </main>
  );
}
