"use client";

import { useState } from "react";
import { api, type QAResponse } from "@/lib/api";
import LegalAidRedirect from "./LegalAidRedirect";

/**
 * C20: Q&A chat panel calling C13, rendering inline citations, confidence
 * label, and a visually distinct "I don't know" state.
 */
export default function QAPanel({ documentId }: { documentId: string }) {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<QAResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk() {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.askQuestion(documentId, question);
      setHistory((h) => [...h, resp]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get an answer");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="qa-panel">
      <h2>Ask a question</h2>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <input
          style={{ flex: 1 }}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="e.g. Is my security deposit too high?"
          aria-label="Question"
        />
        <button className="primary" onClick={handleAsk} disabled={loading}>
          {loading ? "Asking..." : "Ask"}
        </button>
      </div>
      {error && <p style={{ color: "#a94442" }}>{error}</p>}

      {history
        .slice()
        .reverse()
        .map((qa, i) => (
          <div key={i}>
            {qa.guardrail.high_stakes ? (
              <LegalAidRedirect
                message={qa.guardrail.legal_aid_redirect || qa.answer}
              />
            ) : qa.i_dont_know ? (
              <div className="qa-answer idk" data-testid="idk-answer">
                <strong>Q: {qa.question}</strong>
                <p>{qa.answer}</p>
                <em>I don&apos;t know — not styled like a normal answer.</em>
              </div>
            ) : (
              <div className="qa-answer">
                <strong>Q: {qa.question}</strong>
                <p>{qa.answer}</p>
                {qa.citation && <p>Citation: {qa.citation}</p>}
                <span className={`confidence-badge confidence-${qa.confidence}`}>
                  Confidence: {qa.confidence}
                </span>
              </div>
            )}
          </div>
        ))}
    </div>
  );
}
