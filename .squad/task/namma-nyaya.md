# Namma Nyaya — Task Breakdown

## Summary

This breaks the revised build-approach plan for Namma Nyaya into concrete, ordered
coder and deploy tasks for the hackathon MVP slice (rental agreements + offer
letters for migrant tech professionals in Bengaluru). The plan of record is a
Python/FastAPI backend + Next.js/React frontend, using a tiered Google Gemini
model strategy (Flash-class for classification/PII-triage/high-stakes detection,
Pro-class for explanation/red-flag reasoning/cited Q&A/ingestion), Gemini-native
multimodal document understanding as the primary OCR path (validated by a
mandatory day-1 go/no-go spike, with Google Cloud Vision as a documented,
conditional fallback), context-stuffing a small curated legal source set instead
of a vector store, POC-level PII masking applied only before storage/logs, and
deployment to Render (backend) + Vercel (frontend) that must remain reachable
after judging. The backend must be built as a channel-agnostic, resource-oriented
API (documents/sessions/actions), not a web-page-shaped API, per the plan's
locked architectural constraint. All 8 decisions the plan previously left open
are now resolved in the plan itself, so this breakdown carries no unresolved
plan-level blocking decisions forward — see "Notes and assumptions" below for a
small number of lower-level implementation defaults this breakdown had to adopt
to make tasks concrete.

## Source plan

`.squad/planner/namma-nyaya.md` (Revised, 2026-09-23), read together with the
underlying spec at `.squad/specification/namma-nyaya.md` for MVP feature scope.

## Notes and assumptions

The plan's own "Decisions resolved" list (8 items) is fully closed, so there are
no **plan-level** blocking decisions to carry forward. However, the underlying
spec's "Open questions / risks" section flags a few things the plan did not
explicitly resolve, which this breakdown had to make a concrete, hackathon-scoped
call on in order to produce actionable tasks. These are not blocking — they are
called out here so the team can override them if they disagree:

- **Confidence indicator methodology (spec open question, undefined by the plan).**
  Task C13 adopts a simple rule-based indicator (High/Medium/Low based on whether
  an answer is backed by an exact statutory citation, a paraphrased citation, or
  no direct match) rather than a model-self-reported score, purely as a
  buildable default for the time-box.
- **Source curation accuracy review (spec open question, undefined by the plan).**
  Task C9 assumes the team itself hand-verifies the curated excerpts (Contract
  Act, Karnataka Rent Act, Karnataka Shops & Establishments Act) before they're
  used for citations; no external legal review step is assumed to exist within
  the hackathon window.
- **High-stakes trigger detection false negatives (spec open question).** Task C8
  treats this as a "detect obvious cases" MVP bar (arrest/criminal/custody/
  divorce/large-property keywords via Flash-class classification), not a
  rigorously tested detector — flagged in C8's acceptance criteria as a known
  limitation, matching the spec's own framing.
- **Red-flag list wording**: this breakdown uses the spec's own MVP red-flag list
  verbatim (deposit size norms, painting/cleaning deduction clauses, lock-in
  asymmetry, non-compete enforceability under Contract Act Section 27, training
  bond enforceability) rather than a paraphrase, since that is the literal
  in-scope list in the source spec.

## Coder tasks

Backend: Python/FastAPI. Frontend: Next.js/React. All backend endpoints are
resource-oriented (`/documents`, `/sessions`, `/actions`-style paths) per the
plan's locked channel-agnostic constraint — no endpoint should be shaped around
a specific web page or assume a browser-only session/auth model.

| ID | Task | Depends on | Acceptance criteria |
|----|------|------------|----------------------|
| C1 | Backend scaffold: FastAPI project skeleton with resource-oriented routing (`/documents`, `/sessions`, `/actions` namespaces), OpenAPI docs enabled, env-based config loader (Gemini API key, model-tier names as config, not hardcoded), `GET /health`. | none | `GET /health` returns 200 locally; `/docs` renders full OpenAPI schema; no route path or payload shape is web-page-specific. |
| C2 | Frontend scaffold: Next.js app with a two-column layout shell (document viewer + chat/explanation panel), API client module reading backend base URL from an env var, EN/KN language-toggle stub. | none | App builds and runs locally; placeholder layout renders; API client successfully calls backend `/health` and displays the result. |
| C3 | Gemini SDK integration + tiered model wrappers: wire `google-genai` Python SDK with the AI Studio API key from env; build thin "Flash-class call" and "Pro-class call" wrapper functions with model name sourced from config (not hardcoded, per the plan's own caveat that model version strings move quickly). | C1 | A smoke-test call succeeds against both the Flash-class and Pro-class wrappers using only an env var API key; changing the model name requires only a config change, no code edit. |
| C4 | **Day-1 Gemini-Kannada-OCR go/no-go spike (critical path — do first, before any ingestion-dependent feature work).** Assemble 5-10 representative sample documents: clean English, clean Kannada, code-mixed Kannada/English, and at least 2 poor-quality/low-resolution scans. Send each directly to the Gemini Pro-class multimodal endpoint for full text extraction; compare against a human reference transcription; log accuracy and failure modes; record an explicit go/no-go call. | C3 | A written spike log exists with per-document accuracy notes and one explicit go/no-go decision. If "go," C7 proceeds on the Gemini-native path. If "no-go," C5 must run before C7-C13 continue. Nothing downstream should be treated as unblocked until this returns a result. |
| C5 | *(Conditional — only if C4 returns "no-go")* Google Cloud Vision OCR fallback: set up GCP project + billing, wire Vision OCR as a text-extraction pre-processing step, feed its output into the existing Gemini Pro-class wrapper (C3) for downstream classification/explanation instead of raw image/PDF. | C4 (no-go branch) | Re-running C4's sample set through Vision→Gemini shows materially better extraction accuracy; the pipeline is exposed behind the same internal interface as the primary path so C7 doesn't need to know which was used. |
| C6 | PII masking module: regex-based Aadhaar/PAN detection and redaction applied at the point content is written to persistent storage or application logs — explicitly **not** applied before the outbound Gemini call, per the plan's accepted POC-level limitation. | C1 | Unit tests confirm sample Aadhaar/PAN-shaped strings are redacted in anything written to DB/logs; a code comment or doc note records that raw content still reaches Gemini in-flight. |
| C7 | Document ingestion endpoint (`POST /documents`): accept PDF/image upload, route through the locked ingestion pipeline (C4's primary path or C5's fallback), extract text, apply PII masking (C6) before persisting, store text + metadata keyed by document ID. | C4 (or C5 if triggered), C6 | Uploading a sample document returns a document ID; `GET /documents/{id}` returns the masked extracted text; endpoint follows the `/documents` resource pattern. |
| C8 | Classification + high-stakes trigger detection (Flash-class): classify document type (rental agreement vs. offer letter) and scan for high-stakes trigger terms (arrest, criminal charge, custody, divorce, large property value). Known limitation: MVP-level keyword/classification detection, not a rigorously tested detector (see Notes). | C7, C3 | An action endpoint returns a document-type label and a high-stakes flag; a test document containing a high-stakes term is flagged; a plain rental agreement is not. |
| C9 | Curated legal source set assembly: collect and format the hand-curated MVP excerpts (Indian Contract Act Section 27, relevant Karnataka Rent Act provisions, Karnataka Shops & Establishments Act excerpts) into one reusable, citation-labeled context block sized for context-stuffing alongside a document's clauses. | none (can start in parallel with C3/C4) | A versioned source file exists with citation labels (statute + section) per excerpt; confirmed to fit comfortably in the Pro-class context window alongside a typical document's clause text. |
| C10 | Three-level explanation engine (Pro-class): produce one-line gist, clause-by-clause plain-language explanation, and legal-view-with-citations, in English and Kannada, using C3's Pro-class wrapper and C9's source block. | C7, C8, C9 | An action endpoint returns all three levels in both languages for a sample rental agreement and offer letter; legal-view citations reference only sources present in C9's curated set (no fabricated citations). |
| C11 | Red-flag detection engine covering the spec's MVP list: deposit size norms, painting/cleaning deduction clauses, lock-in asymmetry, non-compete enforceability (Contract Act Section 27), training bond enforceability. Rules+retrieval hybrid against C9's source set. | C7, C9, C10 | Running against a sample agreement with at least 2 planted issues correctly flags them with a citation; a clean sample agreement does not produce false flags. |
| C12 | Compare/diff engine: given two document IDs, align clauses and surface differences, highlighting clauses that map to C11's red-flag categories. | C7, C11 | Submitting two sample offer letters (or landlord draft vs. fair-model agreement) returns a structured diff identifying at least differences in deposit amount, notice period, and lock-in terms. |
| C13 | Cited Q&A endpoint: answer grounded only in C9's source set plus the document's own clauses, with a citation, a confidence indicator (rule-based High/Medium/Low per Notes), and an explicit "I don't know" response when ungrounded. | C7, C9 | An in-scope question returns an answer + citation + confidence label; an out-of-scope question returns an explicit "I don't know" rather than a fabricated answer. |
| C14 | Old-to-new law mapping utility: standalone lookup mapping IPC/CrPC/Evidence Act sections to BNS/BNSS/BSA equivalents and back, exposed as its own action endpoint, independent of the document flow. | C1 | A lookup endpoint returns the correct BNS-family equivalent for at least 10 seeded common sections in both directions; works with no document uploaded. |
| C15 | Navigator playbooks: implement the spec's 2-3 MVP playbooks (at minimum: security deposit not returned → legal notice draft + evidence checklist; plus a second, e.g. RERA-style builder delay), returning forum/authority, required documents, a generated draft, rough timeline, rough cost. | C9, C10 | Triggering the "deposit not returned" playbook returns a usable draft demand-letter, document checklist, and named forum; the second playbook works end-to-end too. |
| C16 | Responsible-AI guardrail wiring: standing "information, not advice" disclaimer as API response metadata; when C8's high-stakes flag is true, return a redirect-to-lawyer/legal-aid message (KSLSA/DLSA/NALSA 15100) instead of substantive content; wire C13's "I don't know" as a first-class response shape. | C8, C10, C13 | A high-stakes-flagged document's explanation/Q&A calls return the legal-aid redirect instead of content; normal responses include the standing disclaimer field. |
| C17 | Frontend: document upload + side-by-side viewer + explanation panel wired to live API, with working EN/KN and gist/clause/legal-view toggles. | C2, C7, C10 | Uploading a sample document in-browser shows the original file alongside working explanation toggles, backed by live API calls (not mocked data). |
| C18 | Frontend: red-flag highlighting over the document/explanation view, color-coded per C11's output, with citation shown on hover/click. | C11, C17 | A sample document with planted issues visibly highlights flagged clauses with citation and reasoning on interaction. |
| C19 | Frontend: compare/diff view rendering C12's structured diff side by side. | C12, C17 | Uploading two sample documents and requesting compare renders a side-by-side diff highlighting the differing clauses C12 identified. |
| C20 | Frontend: Q&A chat panel calling C13, rendering inline citations, confidence label, and a visually distinct "I don't know" state. | C13, C17 | An in-scope question shows an answer with citation and confidence label; an out-of-scope question visibly renders as "I don't know," not styled like a normal answer. |
| C21 | Frontend: standalone law-mapping lookup page calling C14, independent of any uploaded document. | C14, C2 | A user can look up an IPC section and see its BNS equivalent without uploading a document. |
| C22 | Frontend: navigator UI letting a user pick a recognized situation and view/download the generated playbook output from C15. | C15, C17 | Selecting "deposit not returned" displays the generated draft letter and checklist from C15. |
| C23 | Frontend: guardrail UX — persistent disclaimer banner on every relevant view, and a distinct "please consult a lawyer / legal aid" screen wired to C16's high-stakes redirect. | C16, C17 | Every document/Q&A view shows the standing disclaimer; a high-stakes-flagged document shows the legal-aid redirect screen instead of an explanation. |
| C24 | End-to-end demo rehearsal: run the full intended narrative (upload → explain → red-flag → compare → Q&A → law-mapping → navigator) against the local full stack; fix integration gaps found. | C17, C18, C19, C20, C21, C22, C23 | The full demo narrative runs start-to-finish with no hidden manual step or console error, using the sample documents planned for judging. |

## Deploy tasks

Target: Render (backend) + Vercel (frontend), must remain reachable after
judging ends, not only during a live demo window.

| ID | Task | Depends on | Acceptance criteria |
|----|------|------------|----------------------|
| D1 | Provision a Render web service for the backend: create service, connect repo, configure build/start commands for the FastAPI app. | C1 | Render service builds and starts from the C1 skeleton; `/health` reachable at the Render URL. |
| D2 | Provision a Vercel project for the frontend: create project, connect repo, configure Next.js build settings. | C2 | Vercel deployment succeeds and serves the C2 skeleton at a public URL. |
| D3 | Environment/secrets configuration: set the Gemini AI Studio API key as a Render env var (never committed); set the backend base URL as a Vercel env var; if C4 triggers C5, also provision GCP service-account credentials as Render secrets. | D1, D2, C4 | Backend on Render makes a live Gemini call using only the configured env var; frontend on Vercel correctly targets the deployed backend URL; no secret is committed to the repo. |
| D4 | CORS / cross-origin wiring: configure FastAPI CORS policy to allow the deployed Vercel origin (plus localhost for dev); confirm the API makes no browser-session or web-only auth assumption, consistent with the channel-agnostic constraint. | D1, D2 | A browser request from the deployed frontend to the deployed backend succeeds with no CORS error. |
| D5 | CI/CD wiring: enable auto-deploy on push to the tracked branch for both Render and Vercel. | D1, D2 | A trivial commit to the tracked branch triggers a new visible deploy on both platforms with no manual redeploy step. |
| D6 | *(Conditional — only if C4 returns "no-go")* GCP project + billing setup for the Cloud Vision fallback: create project, enable billing and the Vision API, generate a service-account key. | C4 (no-go branch) | A live Cloud Vision API call succeeds from the Render-hosted backend using the provisioned credentials. |
| D7 | Cold-start / always-on tier decision: explicitly decide and document whether to accept Render's free-tier cold-start behavior or upgrade to a low-cost always-on instance, based on available budget; configure accordingly. | D1 | A documented decision states which tier is used and why; if free tier is kept, the expected cold-start latency is written down somewhere the demo team will see it. |
| D8 | Deploy backend (feature-complete): deploy once coder-lane endpoints through C16 land on the tracked branch. | D1, D3, D4, D5, C7-C16 | The deployed `/docs` shows the full documents/sessions/actions API surface matching the local build; a live request to each major endpoint (documents, explanation, red-flag, compare, Q&A, law-mapping, navigator) succeeds. |
| D9 | Deploy frontend (feature-complete): deploy once frontend integration tasks through C23 land on the tracked branch. | D2, D3, D4, D5, C17-C23 | The deployed frontend, pointed at the deployed backend, renders the full demo flow (upload through navigator) using only public URLs. |
| D10 | Post-deploy smoke test: from a clean browser/network (not the dev machine), run the full demo narrative against the live URLs. | D8, D9, C24 | The full narrative completes end-to-end against public URLs with no missing-env-var, CORS, or unexpected cold-start surprise. |
| D11 | Post-judging persistence check: after an idle period long enough to trigger Render free-tier spin-down (if that tier was kept), hit the live URL again to confirm automatic wake with no manual intervention; confirm the frontend stays reachable throughout. | D10, D7 | Backend automatically recovers from idle spin-down on next request; frontend never goes fully unreachable; observed cold-start time is recorded for the team. |
| D12 | Demo-day fallback readiness note: confirm the Approach 1 (Streamlit/Gradio) emergency fallback trigger condition and plan are understood by the team, per the plan's own explicit fallback framing — no fallback code built here. | D10 | A short note/runbook exists stating the fallback plan and its trigger condition; team confirms awareness. |

## Status

Draft — 2026-09-23
