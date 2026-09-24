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

---

## 2026-09-24 — Frontend visual restyle pass

### Summary

Restyled the whole Next.js frontend (the C2/C17-C23 coder-lane components
and all four pages) to match the visual design mockup at
`design/Namma Nyaya.html`, per direct instructions from the orchestrating
agent rather than a new line item in `.squad/task/namma-nyaya.md` — this
was a presentation-layer-only pass, not a re-implementation of any coder
task. No API call logic, routes, request/response shapes, or
`frontend/lib/api.ts` request functions were changed. The design's warm
"paper" editorial aesthetic (colors, Source Serif 4 / Public Sans / IBM
Plex Mono / Noto Sans Kannada typography, restrained small-radius
components) was applied via new CSS custom properties in
`frontend/app/globals.css` and `next/font/google` loaders in
`frontend/app/layout.tsx`. All existing upload → explain → red-flag →
compare → Q&A → law-mapping → navigator flows were re-verified working
against both a production build (`npm run build` + `npm run start`) and a
locally running FastAPI backend in mock mode, via real live API calls (not
mocked in the frontend) driven through headless-browser screenshots.

### Source instruction

Direct task from the orchestrating/parent agent (not a `.squad/task/`
breakdown item), read together with `design/Namma Nyaya.html` (rendered via
headless Chrome and Playwright-driven navigation across its four bundled
screens: Document, Compare, Law mapping, Navigator) and the original
coder task breakdown at `.squad/task/namma-nyaya.md` (C2, C17-C23) for
which components/pages this restyling applies to.

### Completed

- **Design tokens.** `frontend/app/globals.css` rewritten with CSS custom
  properties for the full palette (`--color-bg #f5f3ee`, `--color-surface
  #fffdf9`, `--color-surface-soft #efece4`, border/text scales exactly as
  specified), a small border-radius scale (4-12px, `50%` for the circular
  upload icon), and typography tokens. `frontend/app/layout.tsx` now loads
  Source Serif 4, Public Sans, IBM Plex Mono and Noto Sans Kannada via
  `next/font/google` (idiomatic for Next 14 App Router), exposed as
  `--font-serif` / `--font-sans` / `--font-mono` / `--font-kannada` CSS
  variables on `<html>`.
- **`TopNav.tsx`** — restyled to the design's wordmark + Kannada subtitle +
  tab-style nav (active tab as a filled dark pill) + right-side status
  indicator and language toggle. Converted to a client component that
  calls the real `api.health()` (the same call `page.tsx` already made) so
  "Service online" / "Service unreachable" is live on every page, not
  fabricated. Added a new `frontend/components/LanguageProvider.tsx`
  (React context) so the nav's English/ಕನ್ನಡ toggle is a genuine, shared
  site-wide preference — `ExplanationPanel.tsx` now reads/writes that
  context instead of holding its own disconnected local toggle, so
  switching language in the nav updates any open explanation in place.
  `LanguageToggle.tsx`'s own props/behavior (`value`, `onChange`) are
  unchanged, only its visual class names and where it's rendered changed.
- **`DisclaimerBanner.tsx`** — copy updated to the design's exact wording
  ("Information, not advice. Namma Nyaya explains documents. It isn't a
  lawyer and can be wrong."), restyled to the soft-surface banner strip;
  the optional `text` override prop still works unchanged.
- **`DocumentUpload.tsx`** — rebuilt visually as the design's dashed
  drop-zone with a circular "+" icon, plus a new `variant="compact"` mode
  (small "Upload file" / "Use sample: X" pills) for the Compare page's
  side-by-side cards. Added an optional `samples` prop
  (`SampleDocument[]`) — clicking a sample fetches a real static file and
  uploads it through the exact same `api.uploadDocument()` call as a
  manually chosen file (see "Sample documents" below). Existing
  `onUploaded` prop/behavior unchanged.
- **`ExplanationPanel.tsx`, `RedFlagList.tsx`, `QAPanel.tsx`,
  `LegalAidRedirect.tsx`** — restyled to the new token set (mono badges,
  serif headings, warm palette), markup lightly restructured for styling
  hooks (e.g. `.red-flag-head`, `.qa-input-row`) but all props and
  API-calling logic untouched. `LegalAidRedirect.tsx` now also surfaces the
  "Free legal aid: 15100" line from the design.
- **`app/page.tsx` (Document page)** — added the design's hero section
  (serif headline, supporting paragraph, the three numbered 01/02/03 trust
  points, verbatim from the design) shown before a document is uploaded;
  removed the now-redundant inline "Backend health" text (superseded by
  the nav's live status indicator, so the same information isn't shown
  twice in different styles).
- **`app/compare/page.tsx`** — restyled to the design's "Compare two
  documents" layout: dashed Document A/B cards using the new compact
  upload variant with one real sample each, and a dashed
  "Add both documents to see the differences." placeholder box matching
  the design's empty state, shown until both are uploaded.
- **`app/law-mapping/page.tsx`** — restyled to the design's "Old section →
  new section" layout; the free-text "code" filter became a `<select>`
  dropdown (Any/IPC/CrPC/Evidence Act/BNS/BNSS/BSA) purely as a markup
  change — it still calls `api.lookupLawMapping(section, code)` with the
  exact same optional-string parameter, so no API shape changed. Results
  render as the design's row list (mono old code → bold mono new code +
  description) with the design's explanatory footnote about the 1 July
  2024 BNS/BNSS/BSA changeover added as static copy.
- **`app/navigator/page.tsx`** — situation picker changed from generic
  pill buttons to the design's card grid (selected card shown filled dark,
  per the design), with an always-visible "A few facts" panel and a
  design-matching dashed hint box ("Fill in what you know and generate...")
  shown before a situation is picked. Still calls the same
  `listPlaybooks()` / `runPlaybook()` API functions with the same facts
  shape.
- **`Footer.tsx` (new)** — added the design's site-wide footer ("Namma
  Nyaya · Built for Bengaluru · Rental agreements and offer letters only" /
  "Free legal aid: 15100"), rendered once in `app/layout.tsx` so it appears
  on all four pages, matching the design's screenshots of every screen.
- **Sample documents (judgment call, flagged per the task's own
  instructions).** The design shows "try a sample" buttons ("Rental
  agreement · HSR Layout", "Offer letter · Whitefield", "High-stakes
  example", plus "Use sample: HSR Layout" / "Use sample: Koramangala" on
  Compare). Rather than adding non-functional buttons or inventing fake
  copy, real small synthetic PDF documents were generated (via a one-off
  `reportlab` script, not committed as a dependency) and committed as
  static files under `frontend/public/samples/`: `rental-agreement-hsr-
  layout.pdf`, `offer-letter-whitefield.pdf`,
  `rental-agreement-koramangala.pdf`, and `high-stakes-example.pdf`
  (the last containing synthetic arrest/custody/divorce/large-property
  language to exercise the guardrail path). Clicking a sample button fetches
  the real file and uploads it through the same live `POST /documents` call
  as a manual upload (`frontend/lib/samples.ts` centralizes the URLs/labels).
  These are genuinely uploaded and processed by the real backend — nothing
  about them is mocked in the frontend.

### Verification performed

- `npm run build` — succeeds (`✓ Compiled successfully`, all 4 routes
  statically generated, no type errors).
- `npm run lint` — `✔ No ESLint warnings or errors`.
- Rendered `design/Namma Nyaya.html` with headless Chrome and, since it's a
  bundled multi-screen artifact, drove it with Playwright (`chromium`
  launched via `channel="chrome"`, no extra browser download) to click
  through all four nav tabs (Document, Compare, Law mapping, Navigator) and
  screenshot each — all four designs were directly observed, none were
  extrapolated blind.
- Built and started the frontend in production mode (`npm run build` +
  `npm run start`) and ran a local FastAPI backend in `GEMINI_MOCK_MODE`
  (the same offline mode the original C1-C24 pass used, in an ephemeral
  venv removed afterward — `backend/` itself was not modified), then drove
  the running app with Playwright to confirm, via real live API calls: the
  Document page's hero/upload/sample flow producing a real document +
  explanation + red-flags render; the nav's language toggle switching a
  live explanation between English and Kannada; the Compare page's two
  sample uploads producing a real structured diff table; the Navigator
  page's situation cards, facts form, and a fully generated playbook draft
  with a working download button; and the Law-mapping page's dropdown +
  lookup returning a real IPC→BNS row. Screenshots of all of these matched
  the design closely.

### Blocked

None of the coder-lane restyling work was blocked by a missing decision.

### Caveats / things not fully verified

- **High-stakes guardrail redirect could not be exercised end-to-end
  locally.** The backend's `GEMINI_MOCK_MODE` ingestion path (from the
  original C1-C24 build, unmodified here) returns a fixed canned
  "MOCK EXTRACTION" rental-agreement text regardless of which file is
  actually uploaded, so the synthetic `high-stakes-example.pdf` sample
  produced the same generic mock explanation as the other samples in this
  local test rather than triggering the classifier's high-stakes keywords
  and the `LegalAidRedirect` screen. This is a backend mock-mode
  limitation, not a frontend defect: `LegalAidRedirect.tsx`'s rendering
  path is unchanged from the version already covered by the backend's own
  `test_high_stakes_document_gets_legal_aid_redirect` test, and the
  frontend's `guardrail.high_stakes` branch logic in `ExplanationPanel.tsx`
  / `QAPanel.tsx` was not touched beyond styling. Recommend the team
  re-verify the "High-stakes example" sample specifically against the
  live deployed backend (real Gemini key/OCR), where the sample's actual
  arrest/custody/divorce/large-property text should be read for real and
  correctly trigger the redirect.
- **Global language toggle is a judgment call beyond pure restyling.** The
  design shows an English/ಕನ್ನಡ toggle in the top nav with no visible
  backend wiring in the mockup. To avoid adding a decorative, non-functional
  control, this pass lifted the existing (already-functional)
  explanation-language toggle into a shared `LanguageProvider` context so
  the nav's toggle is real and affects any open explanation — a small,
  self-contained structural change (no new API calls, no changed routes),
  flagged here since it goes slightly beyond a pure CSS/markup restyle.
- **"Service online" status dot is new, not purely cosmetic.** Moving the
  existing `api.health()` call from `page.tsx` into `TopNav.tsx` so the
  indicator is live on every page (as the design shows) is a small
  behavioral/structural addition, not just CSS — called out here for
  transparency even though it reuses the exact same existing API call.
- Build/lint were run against this restyled frontend only; the backend's
  own test suite was not re-run (backend directory was not modified,
  consistent with the run instructions).

### Remaining

None outstanding from this restyling instruction. Any further coder-lane
work would come from a new/updated `.squad/task/` breakdown.

### Status

Complete — 2026-09-24 (frontend restyled to match `design/Namma Nyaya.html`
across all four pages; `npm run build` and `npm run lint` both pass; one
guardrail-flow caveat above requires live-backend re-verification by the
team, not fixable from the frontend side).
