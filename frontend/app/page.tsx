"use client";

import { useEffect, useState } from "react";
import { api, type DocumentCreateResponse, type DocumentGetResponse, type ExplanationResponse, type RedFlagResponse } from "@/lib/api";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import DocumentUpload from "@/components/DocumentUpload";
import ExplanationPanel from "@/components/ExplanationPanel";
import RedFlagList from "@/components/RedFlagList";
import QAPanel from "@/components/QAPanel";

export default function HomePage() {
  const [healthStatus, setHealthStatus] = useState<string>("checking...");
  const [document, setDocument] = useState<DocumentGetResponse | null>(null);
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const [redFlags, setRedFlags] = useState<RedFlagResponse | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .health()
      .then((res) => setHealthStatus(res.status))
      .catch(() => setHealthStatus("unreachable"));
  }, []);

  async function handleUploaded(created: DocumentCreateResponse) {
    setError(null);
    setLoadingAnalysis(true);
    try {
      const doc = await api.getDocument(created.id);
      setDocument(doc);
      const [explanationResp, redFlagResp] = await Promise.all([
        api.explainDocument(created.id),
        api.redFlagsForDocument(created.id),
      ]);
      setExplanation(explanationResp);
      setRedFlags(redFlagResp);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoadingAnalysis(false);
    }
  }

  return (
    <main>
      <DisclaimerBanner />
      <div style={{ padding: "1rem 1.5rem 0" }}>
        <p style={{ fontSize: "0.8rem", color: "#666" }}>
          Backend health: <strong>{healthStatus}</strong>
        </p>
        <DocumentUpload onUploaded={handleUploaded} />
        {loadingAnalysis && <p>Analyzing document...</p>}
        {error && <p style={{ color: "#a94442" }}>{error}</p>}
      </div>

      {document && (
        <div className="two-column">
          <div className="panel">
            <h2>Document</h2>
            <p>
              <strong>{document.filename}</strong> ({document.document_type ?? "unclassified"})
            </p>
            <div className="doc-text">{document.masked_text}</div>

            {redFlags && (
              <>
                <h2 style={{ marginTop: "1.5rem" }}>Red flags</h2>
                <RedFlagList flags={redFlags.flags} />
              </>
            )}
          </div>

          <div className="panel">
            {explanation && <ExplanationPanel explanation={explanation} />}
            <hr style={{ margin: "1.5rem 0" }} />
            <QAPanel documentId={document.id} />
          </div>
        </div>
      )}
    </main>
  );
}
