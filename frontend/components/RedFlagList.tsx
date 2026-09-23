"use client";

import { useState } from "react";
import type { RedFlag } from "@/lib/api";

/**
 * C18: red-flag highlighting, color-coded by severity, with citation shown
 * on hover/click (title attribute gives a hover tooltip; clicking expands
 * the full reasoning + citation inline for accessibility on touch devices).
 */
export default function RedFlagList({ flags }: { flags: RedFlag[] }) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (flags.length === 0) {
    return <p>No red flags detected in this document.</p>;
  }

  return (
    <div>
      {flags.map((flag, i) => (
        <div
          key={i}
          className={`red-flag ${flag.severity}`}
          title={`${flag.explanation} — ${flag.citation}`}
          onClick={() => setExpandedIndex(expandedIndex === i ? null : i)}
        >
          <strong>{flag.category.replace(/_/g, " ")}</strong>{" "}
          <span className={`severity-badge severity-${flag.severity}`}>
            {flag.severity}
          </span>
          <div>&ldquo;{flag.clause_excerpt}&rdquo;</div>
          {expandedIndex === i && (
            <div style={{ marginTop: "0.5rem" }}>
              <p>{flag.explanation}</p>
              <p>
                <em>Citation: {flag.citation}</em>
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
