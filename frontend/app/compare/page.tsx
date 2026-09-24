"use client";

import { useState } from "react";
import { api, type CompareResponse, type DocumentCreateResponse } from "@/lib/api";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import DocumentUpload from "@/components/DocumentUpload";
import { COMPARE_SAMPLE_A, COMPARE_SAMPLE_B } from "@/lib/samples";

/**
 * C19: compare/diff view rendering C12's structured diff side by side.
 */
export default function ComparePage() {
  const [docA, setDocA] = useState<DocumentCreateResponse | null>(null);
  const [docB, setDocB] = useState<DocumentCreateResponse | null>(null);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleCompare() {
    if (!docA || !docB) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.compareDocuments(docA.id, docB.id);
      setResult(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Compare failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <DisclaimerBanner />
      <div className="page-shell">
        <h1 className="page-heading">Compare two documents</h1>
        <p className="page-sub">
          Put two rental agreements or two offer letters side by side and see
          which terms differ.
        </p>

        <div className="two-column compare-columns">
          <div className="compare-card">
            <span className="mono-label">Document A</span>
            <DocumentUpload
              variant="compact"
              onUploaded={setDocA}
              samples={[COMPARE_SAMPLE_A]}
            />
            {docA && <p className="hint-text">Uploaded: {docA.filename}</p>}
          </div>
          <div className="compare-card">
            <span className="mono-label">Document B</span>
            <DocumentUpload
              variant="compact"
              onUploaded={setDocB}
              samples={[COMPARE_SAMPLE_B]}
            />
            {docB && <p className="hint-text">Uploaded: {docB.filename}</p>}
          </div>
        </div>

        {!result && (
          <div className="empty-hint-box">
            {docA && docB ? (
              <button className="primary" onClick={handleCompare} disabled={loading}>
                {loading ? "Comparing..." : "Compare"}
              </button>
            ) : (
              <p>Add both documents to see the differences.</p>
            )}
          </div>
        )}
        {error && <p className="error-text">{error}</p>}

        {result && (
          <>
            <button
              className="primary"
              onClick={handleCompare}
              disabled={!docA || !docB || loading}
              style={{ marginBottom: "1rem" }}
            >
              {loading ? "Comparing..." : "Re-compare"}
            </button>
            <table className="diff-table">
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Document A</th>
                  <th>Document B</th>
                  <th>Red-flag category</th>
                </tr>
              </thead>
              <tbody>
                {result.diffs.map((diff) => (
                  <tr key={diff.field} className={diff.differs ? "differs" : ""}>
                    <td>{diff.field.replace(/_/g, " ")}</td>
                    <td>{diff.value_a ?? "—"}</td>
                    <td>{diff.value_b ?? "—"}</td>
                    <td>{diff.red_flag_category ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </main>
  );
}
