"use client";

import { useRef, useState } from "react";
import { api, type DocumentCreateResponse } from "@/lib/api";

/**
 * C17: document upload control, backed by a live POST /documents call
 * (not mocked data).
 */
export default function DocumentUpload({
  onUploaded,
}: {
  onUploaded: (doc: DocumentCreateResponse) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const doc = await api.uploadDocument(file);
      onUploaded(doc);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,image/png,image/jpeg,image/webp"
        onChange={handleFileChange}
        disabled={uploading}
        aria-label="Upload document"
      />
      {uploading && <p>Uploading...</p>}
      {error && <p style={{ color: "#a94442" }}>{error}</p>}
    </div>
  );
}
