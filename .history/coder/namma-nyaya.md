## 2026-09-23

# Namma Nyaya — Coder Status Report

## Summary

Implemented the full coder lane (C1-C24) from `.squad/task/namma-nyaya.md`:
a Python/FastAPI backend (channel-agnostic, resource-oriented API under
`/documents`, `/sessions`, `/actions`) and a Next.js/React frontend, exactly
per the stack the task breakdown and planner specify. All backend logic —
ingestion, PII masking, classification/high-stakes detection, curated legal
source set, three-level explanation, red-flag detection, compare/diff,
cited Q&A with rule-based confidence, the IPC/CrPC/Evidence Act → BNS/BNSS/
BSA lookup, two navigator playbooks, and guardrail wiring — is built and
covered by 30 passing automated pytest tests, all run in an offline
deterministic "mock mode" since this sandbox has no Gemini API key or
verified path to a live model call. The frontend implements all five pages
(document workspace, compare, law-mapping, navigator) wired to live backend
calls (never mocked in the frontend code itself), builds cleanly
(`npm run build`), lints clean (`npm run lint`), and was manually smoke-run
against a live local backend. The one task that is explicitly **not**
validated as instructed is C4, the day-1 Gemini-Kannada-OCR go/no-go spike:
the ingestion call is implemented correctly and a runnable spike harness is
provided, but it has not been executed against a real key or real Kannada
documents, and is clearly marked UNVALIDATED rather than fabricated as
passing. C5 (the conditional Cloud Vision fallback) was correctly left
unbuilt since no "no-go" result exists to trigger it.

## Source task list

`.squad/task/namma-nyaya.md` (Coder tasks C1-C24), read together with
`.squad/planner/namma-nyaya.md` (Revised) and `.squad/specification/namma-nyaya.md`.

## Completed

- **C1 — Backend scaffold.** `backend/app/main.py`, `backend/app/config.py`,
  `backend/app/routers/health.py`. Resource-oriented routing
  (`/documents`, `/sessions`, `/actions`), OpenAPI docs, env-based config
  (Gemini key/model names never hardcoded). Verified: `pytest -q` (30
  passed, includes `test_health.py` checking `GET /health` → 200 and
  `/openapi.json` contains `/health`, `/documents`, `/sessions`, an
  `/actions*` path); also manually ran `uvicorn app.main:app` and confirmed
  `GET /health` → `{"status":"ok"}` and `GET /docs` → 200 live.

- **C2 — Frontend scaffold.** `frontend/` (Next.js 14.2.35 App Router),
  `frontend/lib/api.ts` (API client reading `NEXT_PUBLIC_API_BASE_URL`),
  `frontend/components/LanguageToggle.tsx`, `frontend/app/page.tsx`
  (two-column layout: document/red-flags panel + explanation/Q&A panel).
  Verified: `npm install` + `npm run build` (succeeds, type-checked) +
  `npm run lint` (clean); manually ran `npm run dev` against a live local
  backend and confirmed via `curl` that the page HTML includes the
  "Backend health" status line and that `/compare`, `/law-mapping`,
  `/navigator` all return 200.

- **C3 — Gemini SDK integration + tiered wrappers.** `backend/app/gemini_client.py`
  (`call_flash`, `call_pro`, `call_pro_multimodal`), model names sourced
  from `backend/app/config.py` (`GEMINI_FLASH_MODEL`, `GEMINI_PRO_MODEL` env
  vars) — changing them requires no code edit. **NOT live-verified**: no
  Gemini API key is available in this sandbox, so the real
  `google.genai.Client` call path has not been exercised. An offline
  deterministic mock mode (`GEMINI_MOCK_MODE`, on by default / forced on
  whenever no key is set) lets the rest of the pipeline be built/tested
  without it; every mock response is tagged `mock: true` in its API
  payload so it's never confused with a real result.

- **C4 — Day-1 Gemini-Kannada-OCR go/no-go spike.** **Explicitly not run
  live**, per the run instructions (no key, no network to the Gemini API
  assumed, no real Kannada sample corpus available here). What exists:
  `backend/app/ingestion.py` (correct extraction prompt + multimodal call
  via C3's wrapper + MIME-type validation), `backend/scripts/run_ocr_spike.py`
  (a runnable harness: point it at a directory of sample docs +
  `<name>.reference.txt` transcriptions, it computes a rough accuracy ratio
  per document and appends results), and `backend/docs/c4_ocr_spike_log.md`
  (explicitly marked **UNVALIDATED**, with the exact steps the team must
  run before trusting this on real documents). Per the run instructions,
  downstream tasks were built against the primary "go" (Gemini-native)
  path as a documented assumption, not a verified result.

- **C5 — Conditional Vision fallback.** Correctly **not built** — C5 only
  triggers on a "no-go" result from C4, and no such result exists yet.

- **C6 — PII masking.** `backend/app/pii.py` (regex Aadhaar/PAN
  detect+redact), applied in `backend/app/routers/documents.py` at
  persistence time only — a code comment there and in `pii.py`'s docstring
  records that raw content still reaches Gemini in-flight during ingestion,
  per the plan's accepted limitation. Verified: `tests/test_pii.py` (4
  tests: Aadhaar redacted, PAN redacted, clean text unchanged, detection
  helper).

- **C7 — Document ingestion endpoint.** `POST /documents` /
  `GET /documents/{id}` in `backend/app/routers/documents.py`, using C4's
  primary path + C6's masking before persistence. Verified:
  `tests/test_documents_flow.py` — upload returns an id, `GET` returns
  masked text, unsupported content-type returns 400.

- **C8 — Classification + high-stakes detection.** `backend/app/classification.py`
  (deterministic keyword rules for document type + high-stakes triggers,
  explicitly documented as the task's own accepted "MVP-level, not
  rigorously tested" limitation; also exercises the Flash-class wrapper).
  Verified: plain rental agreement → `high_stakes: false`,
  `document_type: "rental_agreement"`; a document with "arrest" injected →
  `high_stakes: true` (see `test_classify_flags_plain_rental_agreement_as_not_high_stakes`
  and `test_high_stakes_document_gets_legal_aid_redirect`).

- **C9 — Curated legal source set.** `backend/app/legal_sources.py` — 8
  citation-labeled excerpts (Contract Act §§10/27/73/74, Karnataka Rent Act
  deposit/notice/deduction provisions, Karnataka Shops & Establishments Act
  notice provisions), each with an `id`, formatted into one context block
  (`CONTEXT_BLOCK`, a few hundred words — comfortably fits alongside a
  document's clauses in a long-context prompt). Accuracy note documented
  in-module per the task's own "team hand-verifies" assumption.

- **C10 — Three-level explanation engine.** `backend/app/explanation.py`.
  Citations are computed deterministically via keyword matching against
  C9's set (never parsed from free-form model text), which structurally
  guarantees "no fabricated citations" regardless of mock/live mode.
  Verified: `test_explain_returns_three_levels_both_languages_with_citations`
  — gist/clause-by-clause/legal-view all non-empty in both English and
  Kannada, with a non-empty citation list. Kannada output in mock mode is a
  clearly-labeled placeholder, not real translation — documented in the
  module docstring.

- **C11 — Red-flag detection engine.** `backend/app/red_flags.py` —
  deterministic regex/keyword rules for all five spec categories (deposit
  size, painting/cleaning deduction, lock-in asymmetry, non-compete under
  Contract Act s.27, training bond enforceability), each citing a real C9
  source id. Verified: `test_red_flags_detects_planted_issues` (mock
  ingestion text plants a 10-month deposit and an unconditional
  painting/cleaning deduction; both are caught, each with a citation) and
  `test_red_flags_clean_document_has_no_false_flags` (clean 2-month-deposit
  text produces zero flags).

- **C12 — Compare/diff engine.** `backend/app/compare.py` (field extraction
  + diff over deposit months, tenant/landlord notice, lock-in months,
  employee notice). Verified: `test_compare_two_documents_flags_differences`
  — two documents with different deposit/notice/lock-in values correctly
  show `differs: true` with the right `value_a`/`value_b`.

- **C13 — Cited Q&A endpoint.** `backend/app/qa.py` — confidence is
  rule-based (High = question and document both match the same curated
  source; Medium = only one side matches; "I don't know" = the question
  itself matches nothing in the curated set, regardless of what the
  document contains). Verified: in-scope deposit question → citation +
  High/Medium confidence; "What is the capital of France?" → explicit
  `i_dont_know: true`, `citation: null`, never a fabricated answer.

- **C14 — Old-to-new law mapping utility.** `backend/app/law_mapping.py` —
  20 seeded mappings (≥10 required) across IPC→BNS, CrPC→BNSS,
  Evidence Act→BSA, looked up via `GET /actions/law-mapping`. Verified:
  `tests/test_law_mapping.py` + `tests/test_actions.py` — IPC 302 → BNS 103
  and the reverse both resolve correctly, works with zero documents
  uploaded in the test.

- **C15 — Navigator playbooks.** `backend/app/navigator.py` — two full
  playbooks: "security deposit not returned" (legal notice draft + evidence
  checklist + forum + timeline + cost) and "builder possession delay
  (RERA)" (K-RERA complaint draft). Verified:
  `test_navigator_deposit_not_returned_playbook` — draft, checklist, and
  forum all present and populated with supplied facts.

- **C16 — Guardrail wiring.** `backend/app/guardrails.py` +
  `backend/app/models.py` (`GuardrailMeta`, standing disclaimer on every
  response). High-stakes documents get the legal-aid redirect (KSLSA/DLSA/
  NALSA 15100 message) in place of explanation/red-flag/Q&A content.
  Verified: `test_high_stakes_document_gets_legal_aid_redirect`.

- **C17 — Frontend document workspace.** `frontend/app/page.tsx`,
  `frontend/components/DocumentUpload.tsx`, `ExplanationPanel.tsx`. Live
  `POST /documents` → `GET /documents/{id}` → `explain`/`red-flags` calls
  (no mocked frontend data); working EN/KN and gist/clause/legal-view
  toggles. Verified via `npm run build` + manual local run against a live
  backend (page loads, health status renders).

- **C18 — Frontend red-flag highlighting.** `frontend/components/RedFlagList.tsx`
  — color-coded by severity (high/medium/low CSS classes), citation shown
  via hover title attribute and an expand-on-click panel (for touch/
  accessibility).

- **C19 — Frontend compare/diff view.** `frontend/app/compare/page.tsx` —
  upload two documents, table rendering C12's diff with differing rows
  highlighted.

- **C20 — Frontend Q&A panel.** `frontend/components/QAPanel.tsx` — inline
  citation, confidence badge, and a visually distinct dashed/italic
  "I don't know" state (`.qa-answer.idk` CSS class) separate from normal
  answers.

- **C21 — Frontend law-mapping page.** `frontend/app/law-mapping/page.tsx`
  — standalone lookup, no document upload involved.

- **C22 — Frontend navigator UI.** `frontend/app/navigator/page.tsx` — pick
  a playbook, fill in a few facts, view the generated draft/checklist/
  forum, and download the draft as a `.txt` file.

- **C23 — Frontend guardrail UX.** `frontend/components/DisclaimerBanner.tsx`
  (rendered in `frontend/app/layout.tsx` on every page) and
  `frontend/components/LegalAidRedirect.tsx` (rendered in place of content
  by `ExplanationPanel.tsx` and `QAPanel.tsx` whenever the backend's
  `guardrail.high_stakes` is true).

- **C24 — End-to-end demo rehearsal.** Partially done, honestly reported:
  the full narrative is exercised **at the API level** end-to-end by the 30
  passing backend tests (`backend/tests/test_documents_flow.py`,
  `test_actions.py`) covering upload → classify → explain → red-flag →
  compare → Q&A → law-mapping → navigator, plus manual `curl`/local-run
  checks confirming the frontend's four pages load and successfully call
  the live backend (`/health`, `/actions/navigator/playbooks`, etc.). A
  full interactive browser click-through was **not** performed — this
  sandboxed environment has no browser to drive — so this is flagged as the
  one remaining manual step for the team before a live demo, especially
  once a real Gemini key replaces mock mode.

## Blocked

None of C1-C24 are blocked by a missing plan-level decision — the plan's 8
decisions are all locked, matching the task breakdown's own framing. The one
task that could not be *executed* as specified is:

- **C4** — cannot be run to completion in this sandbox (no Gemini API key,
  no verified live network path to the Gemini API, no real Kannada sample
  document corpus). This is an environment constraint, not a design gap:
  the code, prompt, and harness are all in place
  (`backend/app/ingestion.py`, `backend/scripts/run_ocr_spike.py`,
  `backend/docs/c4_ocr_spike_log.md`). **Action required from the team**:
  obtain a live AI Studio key, assemble the 5-10 sample documents (clean
  English, clean Kannada, code-mixed, 2+ low-quality scans), run the spike
  script, and record an actual go/no-go decision before trusting Kannada
  OCR output in a live demo. If the result is "no-go," C5 (Cloud Vision
  fallback) still needs to be built — it was correctly left unbuilt here
  since no "no-go" result exists to justify it.

## Remaining

All 24 coder tasks were attempted and have concrete, testable
implementations in the repo. The only open item is the manual/live
verification work called out above (C3's live smoke test, C4's actual
spike run, and C24's full browser click-through), which requires
credentials/tooling not available in this build environment.

## Other notes for the team

- `frontend`'s `npm audit` flags several Next.js/postcss CVEs even at the
  patched `14.2.35` version used here (many of the listed advisories are
  broad version-range flags, several concerning self-hosted deployment
  configurations not exercised by this build). Not fixed in this pass
  because the available fix (`next@16`) is a breaking major-version change
  outside this task list's scope — worth a deliberate upgrade decision by
  the team before or after judging, not silently done here.
- Backend storage is in-memory only (`backend/app/storage.py`) — documents
  and sessions are lost on process restart. Fine for a hackathon POC; noted
  as a known limitation, not a bug.
- All hand-curated legal content (`backend/app/legal_sources.py`,
  `backend/app/law_mapping.py`) is flagged in-code as needing the team's
  own accuracy review before non-demo use, per the task breakdown's own
  "Notes and assumptions."

## Status

Complete — 2026-09-23 (all C1-C24 attempted; C3/C4/C24 have explicitly
documented manual/live-verification gaps rather than fabricated passing
results; C5 correctly left unbuilt as not-yet-triggered).
