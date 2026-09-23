# Namma Nyaya — Build-Approach Plan

## Summary

This plan turns the MVP scope in `.squad/specification/namma-nyaya.md` (rental agreements + offer letters for migrant tech professionals in Bengaluru, with multilingual OCR ingestion, three-level explanation, red-flag detection, compare/diff, cited Q&A over a small curated source set, an IPC/CrPC/Evidence Act → BNS/BNSS/BSA mapping tool, a 2-3 playbook navigator, and baseline responsible-AI guardrails) into concrete, buildable technical approaches for a time-boxed hackathon. This is a **revision**: the team has now answered all 8 open decisions raised in the prior draft (LLM provider, OCR provider, stack preference, UI approach, retrieval approach, deployment persistence, channel-agnostic architecture, and PII-masking scope), so this version locks those in as confirmed choices rather than presenting them as open trade-offs. The overall shape of the recommendation is unchanged (full web app, context-stuffed RAG over a small curated source set), but the LLM provider is now Google's Gemini family (via an AI Studio API key) instead of Claude/GPT, OCR ingestion leans on Gemini's own native multimodal document understanding rather than a separate OCR API, and deployment/architecture choices now explicitly account for "must stay live after judging" and "channel-agnostic core API" constraints.

## Source spec

`.squad/specification/namma-nyaya.md`

## Candidate approaches

Two overall end-to-end approaches are presented, followed by per-dimension options (OCR, model, retrieval) that apply to both, since those choices are largely independent of which overall approach is picked. **Approach 2 is now the confirmed plan of record** (see Decisions resolved #3-4); Approach 1 remains documented only as an emergency fallback, not a candidate to weigh against Approach 2.

### Approach 1 — Fast-build, Python-only stack (Streamlit/Gradio front end) — EMERGENCY FALLBACK ONLY

- **Backend**: Python, with the RAG/OCR/LLM orchestration logic living directly inside the same app as the UI (no separate API service), or a very thin FastAPI layer if a clean split is wanted later.
- **Frontend**: Streamlit or Gradio. Both can render a two-column layout (document view + chat/explanation panel), file upload widgets, language toggles, and simple highlight rendering (e.g. colored markdown/HTML blocks per clause) with very little UI code.
- **Pros**: By far the fastest path to a working end-to-end demo in a time-boxed hackathon; one language for the whole stack; Python has the richest ecosystem for OCR, PDF parsing, and Indian-language NLP tooling, so ingestion code and demo UI can sit in the same process with no API-contract overhead; Streamlit Community Cloud or a single Render/Railway service is a one-click deploy.
- **Cons**: Visibly less polished than a custom web UI — judges will see a "notebook-style" app rather than a product; harder to do precise clause-highlight overlays directly on a scanned document image; harder to extend into a "real" product later.
- **Complexity**: Low.
- **Status**: The team has confirmed it is explicitly building a full web app, not a notebook-style demo (Decisions resolved #3-4). This approach is retained in the plan **only** as a documented last-resort fallback if Approach 2's plumbing isn't wired end-to-end with enough time left before the demo — it is not the plan of record and should not be started as a parallel track.

### Approach 2 — Full-stack web app (Python/FastAPI backend + React/Next.js frontend) — PLAN OF RECORD

- **Backend**: Python + FastAPI, handling upload intake, PII masking, classification, the RAG/Q&A pipeline (Gemini-based), red-flag/compare logic, and the old-to-new law mapping lookup, exposed as a clean, versioned REST/JSON API consumed by the web frontend.
- **Backend language call**: the team stated no strong stack preference ("anything"), so this plan makes the call for Python/FastAPI over a Node/Next.js-API-routes backend, for three concrete reasons: (1) the OCR fallback path (Google Cloud Vision, if the Gemini-native-ingestion spike fails — see OCR section) has its most mature, best-documented SDK in Python; (2) Google's Gemini Python SDK (`google-genai`) is a first-class, well-maintained client, on par with the JS SDK, so there's no language-driven reason to prefer Node for the Gemini calls themselves; (3) PII-masking/regex work over OCR'd text and any future Indian-language NLP work remains a Python-ecosystem strength. FastAPI specifically is async-friendly (useful for chaining Gemini calls without blocking) and ships first-class OpenAPI docs, useful for a demo judge or teammate to inspect the channel-agnostic API directly (see architectural constraint below).
- **Frontend**: Next.js/React, giving a real side-by-side document viewer (original scan/PDF on one side, clause-by-clause explanation with color-coded highlights on the other), a chat panel for Q&A with inline citations, and a language toggle.
- **Pros**: Much stronger demo polish — a side-by-side annotated document view is a strong visual differentiator for judges and closely matches the spec's description of the explanation/red-flag UX; clean separation between orchestration logic and UI, which directly supports the now-confirmed channel-agnostic API requirement; closer to what a real post-hackathon product would need.
- **Cons**: Two codebases/deploys to wire up (CORS, shared types/contracts, two hosting targets); more hackathon time spent on plumbing before any feature work shows results.
- **Complexity**: Medium-High.

### Backend language alternative worth naming and rejecting: Node/TypeScript full-stack (Next.js API routes)

- A single Next.js app (API routes as the backend, same repo as the frontend) using a JS-native LLM orchestration layer (e.g. Vercel AI SDK, which has native Gemini support) is a real alternative: one language, one repo, one Vercel deploy.
- **Rejected** because: (a) the OCR fallback tooling (Google Cloud Vision, and the broader Indian-language OCR reference landscape — Bhashini, AI4Bharat) is overwhelmingly Python-first; (b) OCR + multi-step Gemini chaining for a full document (ingest → classify → explain → red-flag → cite) can run long, and Vercel's serverless function execution-time limits (short on free/hobby tiers) are a real risk for this pipeline versus a long-running Python process on Render/Railway; (c) it does not clearly outperform Python on any dimension the team said it cares about, since there's no stated language preference to weigh against these two Python-favoring risks.

### Architectural constraint: channel-agnostic core API (locked, from Decisions resolved #7)

The team has confirmed the backend must be designed as a **channel-agnostic API** — a clean separation between the core document/legal-reasoning logic (ingestion, classification, explanation, red-flag, compare, Q&A, law mapping, navigator) and the web frontend that consumes it, so that a future channel (e.g. a WhatsApp bot) could be bolted on later without rewriting the core. This is an explicit constraint for the coder and deploy lanes to respect, not a feature to build now:
- The FastAPI backend's endpoints should be designed around documents/sessions/actions (e.g. `POST /documents`, `GET /documents/{id}/explanation`, `POST /documents/{id}/qa`), not around web-page-specific shapes, and should not assume a browser session or web-only auth model.
- No WhatsApp bot, WhatsApp Business API integration, or additional channel is in scope for this hackathon build — this constraint only shapes how the existing web-facing API is factored, per the spec's own "stretch scope" framing of the WhatsApp bot.

### Model choice (applies to Approach 2) — LOCKED to Google Gemini (Decisions resolved #1)

The team has confirmed the LLM provider is Google AI Studio (Gemini API via an AI Studio API key) — not Claude, not OpenAI. The pipeline still has at least three distinct LLM-shaped jobs with different quality/latency/cost needs, so a **tiered Gemini model strategy** is recommended:

- **Document classification, PII-pattern triage, high-stakes trigger detection** — cheap/fast tasks that don't need top-tier reasoning. A Gemini **Flash-class** model fits (e.g. Gemini 2.5 Flash or whatever the current default fast tier is in AI Studio at build time). Keeps per-request cost and latency low for a live, repeated demo, and Flash-class models are within Google AI Studio's free tier for reasonable hackathon usage volumes.
- **Explanation generation, red-flag reasoning, cited Q&A synthesis, ingestion/OCR-via-multimodal (see OCR section)** — this is where citation discipline, refusal behavior ("I don't know" when ungrounded), and legal-register reasoning quality matter most. A Gemini **Pro-class** model is worth the extra cost/latency here (e.g. Gemini 2.5 Pro or the current top-tier "Pro" model in AI Studio). Its long context window is a specific, concrete advantage for this project — see the Retrieval section below.
- **Embeddings (only if/when a vector store is later added)** — Google's own `text-embedding-004`/`gemini-embedding`-family models (available through the same AI Studio/Gemini API surface) are the natural default if the team ever moves off context-stuffing, since staying on one provider avoids an extra cross-provider integration and Google's embedding models have reasonable multilingual coverage. Not needed for MVP given the context-stuffing decision below.

**Important caveat**: exact Gemini model version names/tiers (e.g. whether "2.5" is still current, or a newer generation has shipped) move quickly and should be re-checked against the live Google AI Studio model picker/docs at build time — do not hard-code a model string into a design doc or code without first confirming it's still listed as available in AI Studio.

### Retrieval / vector store approach for the curated source set — LOCKED to context-stuffing (Decisions resolved #5)

The team confirmed context-stuffing (no vector store) for the small, hand-curated MVP source set, which was already this plan's own recommendation. With the provider now locked to Gemini, this is a specifically strong fit rather than just an MVP shortcut:

- Gemini's long-context models (1.5 Pro historically offered up to ~1M-token context; 2.x-generation Pro models retain very large context windows — confirm the exact current ceiling in AI Studio at build time) make it comfortable to pass the **entire curated source set** (a handful of statutes/sections) plus the full document's clauses directly into a single prompt, with generous headroom left over. This is a genuine, provider-specific advantage of the Gemini choice, not just "it happens to also work."
- Mechanically: skip embeddings/vector DB entirely for MVP; concatenate the curated legal source text (Indian Contract Act excerpts, Karnataka Rent Act provisions, Karnataka Shops & Establishments Act excerpts, etc.) into a system/context block, alongside the document's extracted clauses, and let the Pro-class model cite directly from the supplied text.
- Pros (unchanged from prior draft): removes an entire moving part (embeddings model choice, vector DB, retrieval-quality tuning); arguably improves citation reliability for a small corpus since nothing is missed by an imperfect top-k retrieval step; simpler to build/debug in a hackathon window.
- Cons (unchanged, now explicitly accepted): doesn't scale to the "full production-grade retrieval pipeline over India Code + Karnataka Gazette + Indian Kanoon" the spec names as full-vision scope — this remains an MVP-only shortcut, with "swap in a real vector store + Google embeddings" as the known post-hackathon next step.

### OCR/ASR approach for Kannada + English ingestion — LOCKED to Gemini-native multimodal ingestion, primary (Decisions resolved #2)

No candidate OCR/ASR provider (Bhashini, AI4Bharat, Sarvam, Google Cloud Vision) has actually been spiked/tested against real Kannada legal documents, and the team's only credential is a Google AI Studio API key — not a full GCP project with Document AI/Vision billing configured. Given that, the practical, resource-matched choice is:

- **Primary approach: Gemini-native multimodal document understanding.** The Gemini API accepts images and PDFs directly as input and can extract and reason over the text in a single call — so instead of standing up a separate OCR API/service, the ingestion layer sends the uploaded scan/photo/PDF straight to a Gemini Pro-class model and asks it to both extract the text and (in the same or a chained call) perform classification/explanation. This collapses "OCR" and "understanding" into one step and avoids needing any GCP billing setup at all.
- **This is a real, unvalidated technical bet — spike it on day 1.** The open question is whether Gemini reliably extracts Kannada text (especially code-mixed Kannada/English, and low-quality scans of the kind real rental agreements/sale deeds come in) with acceptable accuracy. This should be the very first thing tested against representative sample documents, before any other feature work depends on it.
- **Documented fallback, not the current plan**: if the day-1 spike shows Gemini's Kannada extraction is unreliable, fall back to Google Cloud Vision OCR as a pre-processing step (Vision extracts clean text, which is then fed into Gemini for classification/explanation/reasoning). This requires setting up GCP billing, which the team does not currently have — so this fallback carries its own setup lead time and should trigger an early go/no-go conversation if the spike fails, not be assumed as a same-day pivot.
- Bhashini, AI4Bharat (self-hosted), and Sarvam AI remain viable *long-term* options per the original spec's own open question, but are explicitly not being pursued for MVP given the team's tooling/credential constraints (no GCP project, no evidence any of them integrate faster than the Gemini-native path) — noted for completeness, not part of the current plan.

### PII masking approach — LOCKED to POC-level, storage/log-time masking (Decisions resolved #8, accepted limitation)

The team confirmed a simple, POC-appropriate approach rather than full engineering rigor:

- Basic PII masking/redaction (Aadhaar/PAN pattern detection at minimum, per the spec) is applied **before persisting anything to storage or logs**.
- Masking is **not** applied before every external API call — meaning the raw (or lightly processed) document text may reach Gemini in-flight for classification/explanation/reasoning, since the ingestion approach above already relies on sending the raw document image/PDF to Gemini for native extraction, which is inherently in tension with pre-LLM-call masking anyway.
- **This is accepted as a documented limitation, not a silent gap.** A production version of Namma Nyaya would need PII masking (or at minimum a data-processing agreement/retention-terms review) before any external LLM call too, given the DPDP Act sensitivity the spec itself calls out. This plan records that trade-off explicitly so it doesn't get lost by the task-breakdown stage: the hackathon build sends full document content (including any embedded PII) to Google's Gemini API in-flight, and only masks before the app's own storage/logs.

### Deployment target — must stay live after judging (Decisions resolved #6)

The team confirmed the deployed demo must remain reachable after judging ends, not just during a live demo window — this rules out anything dependent on a presenter's laptop staying on, and pushes toward hosting that doesn't require anyone to manually keep it alive.

- **Backend**: Render (or Railway) free/low-cost web service hosting the FastAPI app. Render's free tier will spin a service down after a period of inactivity, which is a real trade-off — but it wakes automatically on the next incoming request rather than requiring anyone to manually restart or redeploy it, so it still satisfies "stays live without a laptop," just with a cold-start latency penalty (typically tens of seconds) on the first request after idle. Given the cost constraints implied by choosing the AI-Studio-free-tier LLM path in the first place, this trade-off is accepted for the POC; if a few dollars/month is available, a low-cost always-on tier (Render's paid instance tier, Railway's hobby plan, or a small Fly.io machine) removes the cold-start behavior entirely and is worth it if judges are likely to click the link days after the event.
- **Frontend**: Vercel (Next.js). Vercel's hobby tier serves the frontend persistently without the same kind of full spin-down behavior, and remains reachable indefinitely under normal free-tier usage.
- **Local-only fallback**: not viable given the "must stay live after judging" constraint — dropped from consideration as a primary target, kept only as a rehearsed fallback for live-demo-network issues on the day itself, not as the persistent, judge-revisitable deployment.
- **Recommendation**: Render (backend, free tier accepted with documented cold-start trade-off, upgrade to a paid always-on tier if budget allows) + Vercel (frontend) as the deployment target.

## Recommended approach

**Approach 2 (Python/FastAPI backend + Next.js/React frontend), designed as a channel-agnostic core API; Gemini-native multimodal document understanding as the primary ingestion/OCR layer (spiked on day 1, with Google Cloud Vision as a documented fallback requiring GCP billing setup); a tiered Gemini model strategy (Flash-class for classification/PII-triage/high-stakes detection, Pro-class for explanation/red-flag reasoning/cited Q&A synthesis and for ingestion); context-stuffing the curated MVP source set directly into Gemini's long context window instead of a vector store; POC-level PII masking applied before storage/logs only (not before external LLM calls, documented as an accepted limitation); deployed as Render (backend) + Vercel (frontend), accepting Render free-tier cold-start behavior as the cost-appropriate trade-off for a demo that must stay live after judging.**

Rationale: the spec's differentiators (side-by-side compare/diff, clause-level highlighting, cited Q&A) are inherently visual and benefit from a real document-viewer UI rather than a notebook-style app. Gemini as the single LLM provider is now a locked constraint, and its long-context Pro-class models are a specifically good match for both the context-stuffing retrieval approach and native multimodal document ingestion, letting the team skip both a separate OCR API and a vector store — collapsing two of the plan's riskiest infrastructure decisions into "one provider, two model tiers." The channel-agnostic API constraint costs little extra effort if the FastAPI layer is designed around resource-oriented endpoints from the start, and pays off if a WhatsApp channel is ever pursued post-hackathon. The remaining real risk is the unvalidated Gemini-Kannada-OCR bet, which is why it's called out as the literal first thing to test.

**Explicit fallback**: if the team is more than ~1/3 through the time-box and the full-stack plumbing (Approach 2) isn't yet wired end-to-end, fall back to Approach 1 (Streamlit/Gradio, Python-only) rather than risk a non-functional demo — a less polished but fully working demo beats a polished but broken one.

## Decisions resolved

All 8 decisions raised in the prior draft have been answered by the team and are now locked into this plan as described above; nothing is left open for the task-breakdown stage from this list:

1. **LLM provider/model**: Google AI Studio (Gemini API). Tiered Flash/Pro strategy as detailed above.
2. **OCR/ASR provider for Kannada**: No candidate previously tested; MVP uses Gemini's native multimodal document understanding as the ingestion/OCR layer, validated via a mandatory day-1 spike against real Kannada scans, with Google Cloud Vision (requires GCP billing setup) as the documented fallback if the spike fails.
3. **Team stack preference**: No strong preference stated ("anything"), but the team confirmed it is building a full web app, not a notebook-style demo.
4. **UI approach**: Full web app confirmed as the plan of record; Streamlit/Gradio (Approach 1) retained only as an emergency, time-box-triggered fallback, not a parallel candidate.
5. **Retrieval approach**: Context-stuffing the curated MVP source set into Gemini's context window, no vector store — confirmed, and now specifically justified by Gemini's long-context Pro-class models.
6. **Deployment**: Must stay live after judging, not just during the demo. Render (backend, free tier with accepted cold-start trade-off, or a low-cost always-on tier if budget allows) + Vercel (frontend).
7. **Architecture**: Core backend must be built as a channel-agnostic API, cleanly separated from the web frontend, so a future channel (e.g. WhatsApp) could be added later without a rewrite — the WhatsApp bot itself remains out of MVP scope.
8. **PII masking**: POC-level — basic masking/redaction before persisting to storage/logs only, not before every external API call. Documented as an accepted limitation; a production version would need masking (or reviewed data-handling terms) before any external LLM call too, per the DPDP Act sensitivity the spec calls out.

## Status

Revised — 2026-09-23
