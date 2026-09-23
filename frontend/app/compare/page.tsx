"use client";

import { useState } from "react";
import { api, type CompareResponse, type DocumentCreateResponse } from "@/lib/api";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import DocumentUpload from "@/components/DocumentUpload";

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
      <div style={{ padding: "1.5rem" }}>
        <h1>Compare documents</h1>
        <div className="two-column" style={{ padding: 0 }}>
          <div className="panel">
            <h2>Document A</h2>
            <DocumentUpload onUploaded={setDocA} />
            {docA && <p>Uploaded: {docA.filename}</p>}
          </div>
          <div className="panel">
            <h2>Document B</h2>
            <DocumentUpload onUploaded={setDocB} />
            {docB && <p>Uploaded: {docB.filename}</p>}
          </div>
        </div>

        <button
          className="primary"
          onClick={handleCompare}
          disabled={!docA || !docB || loading}
        >
          {loading ? "Comparing..." : "Compare"}
        </button>
        {error && <p style={{ color: "#a94442" }}>{error}</p>}

        {result && (
          <table className="diff-table" style={{ marginTop: "1.5rem" }}>
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
        )}
      </div>
    </main>
  );
}
