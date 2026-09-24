"use client";

import { useState } from "react";
import { api, type DocumentCreateResponse, type DocumentGetResponse, type ExplanationResponse, type RedFlagResponse } from "@/lib/api";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import DocumentUpload from "@/components/DocumentUpload";
import ExplanationPanel from "@/components/ExplanationPanel";
import RedFlagList from "@/components/RedFlagList";
import QAPanel from "@/components/QAPanel";
import { DOCUMENT_PAGE_SAMPLES } from "@/lib/samples";

export default function HomePage() {
  const [document, setDocument] = useState<DocumentGetResponse | null>(null);
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const [redFlags, setRedFlags] = useState<RedFlagResponse | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

      {!document && (
        <section className="hero">
          <div className="hero-copy">
            <h1 className="hero-heading">
              Understand your rental agreement or offer letter before you sign it.
            </h1>
            <p className="hero-sub">
              Upload the document. We&apos;ll explain it in plain English or
              Kannada, flag the clauses that usually cause trouble in
              Bengaluru, and answer your questions with the law behind each
              answer.
            </p>
            <ol className="trust-list">
              <li>
                <span className="trust-index">01</span>
                <span>We mask Aadhaar and PAN numbers before anything is saved.</span>
              </li>
              <li>
                <span className="trust-index">02</span>
                <span>Red flags are checked against Karnataka and central law.</span>
              </li>
              <li>
                <span className="trust-index">03</span>
                <span>If we can&apos;t back an answer with a source, we say so.</span>
              </li>
            </ol>
          </div>

          <div className="hero-upload">
            <DocumentUpload onUploaded={handleUploaded} samples={DOCUMENT_PAGE_SAMPLES} />
          </div>
        </section>
      )}

      <div className="page-shell">
        {loadingAnalysis && <p className="hint-text">Analyzing document...</p>}
        {error && <p className="error-text">{error}</p>}
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
                <h2 className="section-heading">Red flags</h2>
                <RedFlagList flags={redFlags.flags} />
              </>
            )}
          </div>

          <div className="panel">
            {explanation && <ExplanationPanel explanation={explanation} />}
            <hr className="divider" />
            <QAPanel documentId={document.id} />
          </div>
        </div>
      )}
    </main>
  );
}
