/**
 * API client module (C2). Reads the backend base URL from an env var
 * (NEXT_PUBLIC_API_BASE_URL) rather than hardcoding it, so the deploy lane
 * can point this at the deployed Render URL without a code change.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface GuardrailMeta {
  disclaimer: string;
  high_stakes: boolean;
  legal_aid_redirect: string | null;
}

export interface HealthResponse {
  status: string;
}

export interface DocumentCreateResponse {
  id: string;
  filename: string;
  content_type: string;
  created_at: string;
  guardrail: GuardrailMeta;
}

export interface DocumentGetResponse {
  id: string;
  filename: string;
  content_type: string;
  masked_text: string;
  document_type: string | null;
  high_stakes: boolean | null;
  created_at: string;
}

export interface ClassifyResponse {
  document_id: string;
  document_type: string;
  high_stakes: boolean;
  high_stakes_reasons: string[];
  guardrail: GuardrailMeta;
  model_used: string;
  mock: boolean;
}

export interface ExplanationLevels {
  gist: string;
  clause_by_clause: string;
  legal_view: string;
  citations: string[];
}

export interface ExplanationResponse {
  document_id: string;
  english: ExplanationLevels;
  kannada: ExplanationLevels;
  guardrail: GuardrailMeta;
  model_used: string;
  mock: boolean;
}

export interface RedFlag {
  category: string;
  severity: "high" | "medium" | "low";
  clause_excerpt: string;
  explanation: string;
  citation: string;
}

export interface RedFlagResponse {
  document_id: string;
  flags: RedFlag[];
  guardrail: GuardrailMeta;
}

export interface ClauseDiff {
  field: string;
  value_a: string | null;
  value_b: string | null;
  differs: boolean;
  red_flag_category: string | null;
}

export interface CompareResponse {
  document_id_a: string;
  document_id_b: string;
  diffs: ClauseDiff[];
  guardrail: GuardrailMeta;
}

export interface QAResponse {
  document_id: string;
  question: string;
  answer: string;
  citation: string | null;
  confidence: "High" | "Medium" | "Low" | "N/A";
  i_dont_know: boolean;
  guardrail: GuardrailMeta;
}

export interface LawMappingItem {
  old_code: string;
  old_section: string;
  new_code: string;
  new_section: string;
  description: string;
}

export interface LawMappingResponse {
  query: string;
  results: LawMappingItem[];
}

export interface NavigatorPlaybookSummary {
  id: string;
  title: string;
  description: string;
}

export interface NavigatorPlaybookResponse {
  id: string;
  title: string;
  forum: string;
  required_documents: string[];
  draft: string;
  timeline: string;
  cost: string;
  guardrail: GuardrailMeta;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/health"),

  uploadDocument: (file: File, sessionId?: string) => {
    const form = new FormData();
    form.append("file", file);
    if (sessionId) form.append("session_id", sessionId);
    return request<DocumentCreateResponse>("/documents", {
      method: "POST",
      body: form,
    });
  },

  getDocument: (id: string) =>
    request<DocumentGetResponse>(`/documents/${id}`),

  classifyDocument: (id: string) =>
    request<ClassifyResponse>(`/documents/${id}/actions/classify`, {
      method: "POST",
    }),

  explainDocument: (id: string) =>
    request<ExplanationResponse>(`/documents/${id}/actions/explain`, {
      method: "POST",
    }),

  redFlagsForDocument: (id: string) =>
    request<RedFlagResponse>(`/documents/${id}/actions/red-flags`, {
      method: "POST",
    }),

  askQuestion: (id: string, question: string, sessionId?: string) =>
    request<QAResponse>(`/documents/${id}/actions/qa`, {
      method: "POST",
      body: JSON.stringify({ question, session_id: sessionId }),
    }),

  compareDocuments: (documentIdA: string, documentIdB: string) =>
    request<CompareResponse>("/actions/compare", {
      method: "POST",
      body: JSON.stringify({
        document_id_a: documentIdA,
        document_id_b: documentIdB,
      }),
    }),

  lookupLawMapping: (section: string, code?: string) => {
    const params = new URLSearchParams({ section });
    if (code) params.set("code", code);
    return request<LawMappingResponse>(`/actions/law-mapping?${params.toString()}`);
  },

  listPlaybooks: () =>
    request<NavigatorPlaybookSummary[]>("/actions/navigator/playbooks"),

  runPlaybook: (id: string, facts: Record<string, string>) =>
    request<NavigatorPlaybookResponse>(`/actions/navigator/${id}`, {
      method: "POST",
      body: JSON.stringify(facts),
    }),
};
