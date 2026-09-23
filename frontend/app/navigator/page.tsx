"use client";

import { useEffect, useState } from "react";
import {
  api,
  type NavigatorPlaybookResponse,
  type NavigatorPlaybookSummary,
} from "@/lib/api";
import DisclaimerBanner from "@/components/DisclaimerBanner";

/**
 * C22: navigator UI letting a user pick a recognized situation and
 * view/download the generated playbook output from C15.
 */
export default function NavigatorPage() {
  const [playbooks, setPlaybooks] = useState<NavigatorPlaybookSummary[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [facts, setFacts] = useState<Record<string, string>>({});
  const [result, setResult] = useState<NavigatorPlaybookResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api
      .listPlaybooks()
      .then(setPlaybooks)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load playbooks"));
  }, []);

  async function handleRun() {
    if (!selected) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.runPlaybook(selected, facts);
      setResult(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Playbook failed");
    } finally {
      setLoading(false);
    }
  }

  function handleDownload() {
    if (!result) return;
    const blob = new Blob([result.draft], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${result.id}-draft.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main>
      <DisclaimerBanner />
      <div style={{ padding: "1.5rem", maxWidth: 800 }}>
        <h1>Navigator — what do I do now?</h1>
        <div className="toggle-group">
          {playbooks.map((p) => (
            <button
              key={p.id}
              className={`toggle ${selected === p.id ? "active" : ""}`}
              onClick={() => {
                setSelected(p.id);
                setResult(null);
              }}
              type="button"
            >
              {p.title}
            </button>
          ))}
        </div>
        {selected && (
          <div className="panel">
            <p>{playbooks.find((p) => p.id === selected)?.description}</p>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxWidth: 400 }}>
              <input
                placeholder="Your name / tenant name"
                onChange={(e) => setFacts((f) => ({ ...f, tenant_name: e.target.value, buyer_name: e.target.value }))}
              />
              <input
                placeholder="Other party name (landlord/builder)"
                onChange={(e) => setFacts((f) => ({ ...f, landlord_name: e.target.value, builder_name: e.target.value }))}
              />
              <input
                placeholder="Deposit amount / project name"
                onChange={(e) => setFacts((f) => ({ ...f, deposit_amount: e.target.value, project_name: e.target.value }))}
              />
            </div>
            <button className="primary" onClick={handleRun} disabled={loading} style={{ marginTop: "0.75rem" }}>
              {loading ? "Generating..." : "Generate playbook"}
            </button>
          </div>
        )}
        {error && <p style={{ color: "#a94442" }}>{error}</p>}

        {result && (
          <div className="panel" style={{ marginTop: "1rem" }}>
            <h2>{result.title}</h2>
            <p>
              <strong>Forum:</strong> {result.forum}
            </p>
            <p>
              <strong>Timeline:</strong> {result.timeline}
            </p>
            <p>
              <strong>Cost:</strong> {result.cost}
            </p>
            <h3>Required documents</h3>
            <ul>
              {result.required_documents.map((d, i) => (
                <li key={i}>{d}</li>
              ))}
            </ul>
            <h3>Generated draft</h3>
            <div className="doc-text">{result.draft}</div>
            <button className="primary" onClick={handleDownload} style={{ marginTop: "0.75rem" }}>
              Download draft
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
