"use client";

import { useState } from "react";
import { api, type LawMappingResponse } from "@/lib/api";
import DisclaimerBanner from "@/components/DisclaimerBanner";

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
      const resp = await api.lookupLawMapping(section.trim(), code.trim() || undefined);
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
      <div style={{ padding: "1.5rem", maxWidth: 700 }}>
        <h1>IPC/CrPC/Evidence Act ↔ BNS/BNSS/BSA lookup</h1>
        <p>Look up an old or new section number — no document upload needed.</p>
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
          <input
            placeholder="Section, e.g. 302"
            value={section}
            onChange={(e) => setSection(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLookup()}
          />
          <input
            placeholder="Code (optional), e.g. IPC or BNS"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
          <button className="primary" onClick={handleLookup} disabled={loading}>
            {loading ? "Looking up..." : "Look up"}
          </button>
        </div>
        {error && <p style={{ color: "#a94442" }}>{error}</p>}

        {result && (
          <div className="panel">
            {result.results.length === 0 ? (
              <p>No mapping found for &quot;{result.query}&quot;.</p>
            ) : (
              <ul>
                {result.results.map((m, i) => (
                  <li key={i}>
                    <strong>
                      {m.old_code} {m.old_section}
                    </strong>{" "}
                    ↔{" "}
                    <strong>
                      {m.new_code} {m.new_section}
                    </strong>
                    — {m.description}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
