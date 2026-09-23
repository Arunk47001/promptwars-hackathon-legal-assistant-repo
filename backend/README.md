# Namma Nyaya — Backend (FastAPI)

Channel-agnostic, resource-oriented API for the Namma Nyaya hackathon MVP
(rental agreements + offer letters). See `.squad/specification/namma-nyaya.md`,
`.squad/planner/namma-nyaya.md`, and `.squad/task/namma-nyaya.md` for full
context — this README only covers running/testing this backend.

## Setup

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate   # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

By default `.env.example` ships with `GEMINI_MOCK_MODE=true` and no API key,
so the app runs fully offline against deterministic mock Gemini responses —
useful for local dev/testing without a key or network access. **This mock
mode is a development/testing convenience only.** No claim is made that the
mocked outputs reflect real Gemini quality/accuracy — every mock response is
tagged `mock: true` in its API payload.

To use real Gemini calls:
1. Get a Google AI Studio API key.
2. Set `GEMINI_API_KEY=<your key>` and `GEMINI_MOCK_MODE=false` in `.env`.
3. Re-run the smoke test / spike scripts described below.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

- `GET /health` → `{"status": "ok"}`
- `GET /docs` → full OpenAPI schema (Swagger UI)

## Test

```bash
pytest -q
```

All 30 tests pass in offline mock mode (no network/API key required). They
cover: health/OpenAPI shape, PII masking regexes, the law-mapping lookup
table, the full document flow (upload → classify → explain → red-flags →
Q&A) against the mock ingestion output, compare/diff, navigator playbooks,
and guardrail high-stakes redirect wiring.

## What is NOT live-tested here

This sandboxed build environment has no Gemini API key and the live-call
branches of `app/gemini_client.py` have **not** been exercised against the
real Gemini API. Specifically untested-live:

- `call_flash` / `call_pro` real-model smoke test (C3's own acceptance
  criteria explicitly calls for this against a real key).
- The C4 Kannada-OCR go/no-go spike (see `docs/c4_ocr_spike_log.md` —
  explicitly marked UNVALIDATED, with a runnable harness at
  `scripts/run_ocr_spike.py` for the team to execute once a key + sample
  Kannada documents are available).
- Real (non-mock) three-level explanation, red-flag reasoning quality, and
  cited Q&A synthesis quality — the *plumbing* for all of these is built and
  unit-tested against deterministic rule-based/mock logic, but real model
  output quality (especially Kannada) has not been human-reviewed.

Do not treat this backend as demo-ready against real documents until the
above have been manually verified with a live key.

## API surface (resource-oriented, per the channel-agnostic constraint)

- `POST /sessions`, `GET /sessions/{id}`
- `POST /documents` (multipart upload), `GET /documents`, `GET /documents/{id}`
- `POST /documents/{id}/actions/classify`
- `POST /documents/{id}/actions/explain`
- `POST /documents/{id}/actions/red-flags`
- `POST /documents/{id}/actions/qa`
- `POST /actions/compare`
- `GET /actions/law-mapping?section=...&code=...`
- `GET /actions/navigator/playbooks`, `POST /actions/navigator/{id}`

No endpoint assumes a browser session or web-only auth model, per the plan's
locked channel-agnostic architecture constraint.

## Known, documented limitations (not bugs)

- **In-memory storage only** — documents/sessions are lost on restart. Fine
  for a hackathon POC; swap for a real DB before any production use.
- **PII masking is post-Gemini-call, pre-storage only** (`app/pii.py`) — raw
  document content (including any embedded Aadhaar/PAN) reaches Gemini
  in-flight during ingestion. This is an explicitly accepted POC-level
  limitation per the plan (Decisions resolved #8), not an oversight.
- **Curated legal sources and law-mapping table are hand-curated, not
  independently legally reviewed** (`app/legal_sources.py`,
  `app/law_mapping.py`) — verify before any non-demo use.
- **High-stakes detection is deliberately blunt** (`app/classification.py`)
  — obvious-keyword MVP bar only, not a rigorously tested detector, per the
  task breakdown's own framing.
