"use client";

import { useRef, useState } from "react";
import { api, type DocumentCreateResponse } from "@/lib/api";

/**
 * C17: document upload control, backed by a live POST /documents call
 * (not mocked data).
 *
 * Supports two visual variants to match the design:
 *  - "dropzone" (default): the big bordered drop-zone used on the document
 *    workspace page, with an "OR TRY A SAMPLE" row of sample-document pills.
 *  - "compact": the small "Upload file" / "Use sample: X" pill pair used
 *    side by side on the compare page.
 *
 * Sample documents are real, small synthetic PDFs served from
 * /public/samples and uploaded through the exact same api.uploadDocument
 * call as a manually chosen file — never mocked/fabricated data.
 */
export interface SampleDocument {
  label: string;
  url: string;
  filename: string;
}

export default function DocumentUpload({
  onUploaded,
  variant = "dropzone",
  title = "Upload a rental agreement or offer letter",
  subtitle = "PDF, PNG, JPEG or WebP · up to 10 MB",
  samples = [],
}: {
  onUploaded: (doc: DocumentCreateResponse) => void;
  variant?: "dropzone" | "compact";
  title?: string;
  subtitle?: string;
  samples?: SampleDocument[];
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function uploadFile(file: File) {
    setUploading(true);
    setError(null);
    try {
      const doc = await api.uploadDocument(file);
      onUploaded(doc);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    await uploadFile(file);
    if (inputRef.current) inputRef.current.value = "";
  }

  async function handleSampleClick(sample: SampleDocument) {
    if (uploading) return;
    setError(null);
    setUploading(true);
    try {
      const res = await fetch(sample.url);
      if (!res.ok) throw new Error(`Could not load sample (${res.status})`);
      const blob = await res.blob();
      const file = new File([blob], sample.filename, {
        type: blob.type || "application/pdf",
      });
      const doc = await api.uploadDocument(file);
      onUploaded(doc);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sample upload failed");
    } finally {
      setUploading(false);
    }
  }

  const hiddenInput = (
    <input
      ref={inputRef}
      type="file"
      accept="application/pdf,image/png,image/jpeg,image/webp"
      onChange={handleFileChange}
      disabled={uploading}
      aria-label="Upload document"
      className="visually-hidden"
    />
  );

  if (variant === "compact") {
    return (
      <div className="compact-upload">
        {hiddenInput}
        <div className="compact-upload-actions">
          <button
            type="button"
            className="pill-btn-outline"
            onClick={() => inputRef.current?.click()}
            disabled={uploading}
          >
            Upload file
          </button>
          {samples.map((sample) => (
            <button
              key={sample.label}
              type="button"
              className="pill-btn"
              onClick={() => handleSampleClick(sample)}
              disabled={uploading}
            >
              {sample.label}
            </button>
          ))}
        </div>
        {uploading && <p className="hint-text">Uploading…</p>}
        {error && <p className="error-text">{error}</p>}
      </div>
    );
  }

  return (
    <div>
      <div
        className="upload-card"
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
      >
        {hiddenInput}
        <span className="upload-icon-btn" aria-hidden="true">
          +
        </span>
        <p className="upload-title">{title}</p>
        <p className="upload-subtitle">{subtitle}</p>
        {uploading && <p className="hint-text">Uploading…</p>}
        {error && <p className="error-text">{error}</p>}
      </div>

      {samples.length > 0 && (
        <div className="samples-row">
          <span className="samples-label">OR TRY A SAMPLE</span>
          <div className="samples-buttons">
            {samples.map((sample) => (
              <button
                key={sample.label}
                type="button"
                className="pill-btn"
                onClick={() => handleSampleClick(sample)}
                disabled={uploading}
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
