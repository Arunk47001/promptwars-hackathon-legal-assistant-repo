# C4 — Gemini-Kannada-OCR go/no-go spike log

Status: **PRELIMINARY POSITIVE SIGNAL (2026-09-23) — real live API confirmed,
but only against a synthetic clean image, not a real scan. Still not a full
go/no-go per the original spike protocol.**

This is a required "day-1 go/no-go spike" per the task breakdown
(`.squad/task/namma-nyaya.md`, task C4): before building any
ingestion-dependent feature (C7 onward), the team must send 5-10
representative sample documents (clean English, clean Kannada, code-mixed
Kannada/English, and at least 2 poor-quality/low-resolution scans) through
the Gemini Pro-class multimodal path, compare the output against a human
reference transcription, and record an explicit go/no-go call.

## Why this is not filled in

This implementation pass was done in a sandboxed environment with:
- No Gemini API key (`GEMINI_API_KEY` unset).
- No real Kannada rental-agreement/sale-deed sample corpus available.

So the spike **could not actually be executed** here. Fabricating a "go"
result would violate the explicit instruction not to claim a passing test
that didn't run.

## What was built instead

- `backend/app/ingestion.py` — the real ingestion call (extraction prompt,
  multimodal request via `app.gemini_client.call_pro_multimodal`, MIME-type
  validation), ready to run the instant a real key + samples are available.
- `backend/scripts/run_ocr_spike.py` — a runnable harness: point it at a
  directory of sample documents + `<name>.reference.txt` human
  transcriptions, and it computes a per-document rough accuracy ratio
  (difflib character-similarity — a cheap proxy, not a rigorous OCR metric)
  and appends a results table to this file.
- `backend/app/gemini_client.py`'s offline mock mode, so the rest of the
  pipeline (C7 ingestion endpoint, C8 classification, C10 explanation, etc.)
  can be built and integration-tested locally without waiting on this spike
  or a live key — mock responses are clearly labeled `mock: true` in every
  API response so they're never confused with a real result.

## Assumption made to keep the task list moving

Per the run instructions for this build pass, downstream tasks (C7-C13,
C15-C16) are implemented against the **primary Gemini-native path** (the
"go" branch), since:
1. That is the plan's stated primary/recommended path.
2. No spike result exists yet to justify branching to C5 (Cloud Vision
   fallback), and C5 is explicitly conditional on a "no-go" result.

**This is a documented assumption, not a verified outcome.** Before any real
demo or judging, the team MUST:
1. Obtain a Google AI Studio API key, set `GEMINI_API_KEY` and
   `GEMINI_MOCK_MODE=false` in `backend/.env`.
2. Assemble the 5-10 sample documents described above (a real scanned
   Kannada rental agreement or sale deed is the critical one to get right).
3. Run `python backend/scripts/run_ocr_spike.py --samples-dir <dir>`.
4. Manually review the accuracy ratios and failure modes, and write the
   go/no-go decision into a new dated entry below.
5. If the result is "no-go," implement C5 (Cloud Vision fallback) before
   trusting C7-C13's output on Kannada documents.

## Spike run log

### Ad hoc live check — 2026-09-23

A real Google AI Studio key was provided. Before running the full protocol
below (which still needs a real scanned document corpus), we ran a quick
sanity check directly against the live API to confirm the key works and the
model can read Kannada at all:

- **Key validity**: confirmed working. `gemini-2.5-flash` / `gemini-2.5-pro`
  (the model names originally configured) are **retired for new users** as of
  this date — the API returns 404 with a redirect hint. Config updated to
  `GEMINI_FLASH_MODEL=gemini-3.6-flash` (confirmed working) and
  `GEMINI_PRO_MODEL=gemini-pro-latest` (confirmed as a valid name — it
  returned 429 quota-exceeded on the free tier, not 404, so the name is
  correct; re-verify if it starts 404'ing later). **Re-check both against the
  live AI Studio model picker before the demo** — these names may drift
  again.
- **Test input**: a synthetically rendered PNG (not a real scan) containing a
  code-mixed Kannada/English mini rental-agreement excerpt (security deposit,
  tenant name, lock-in period, notice period), rendered with the Windows
  `Nirmala.ttc` Indic font — clean, high-contrast, no skew/noise/handwriting.
- **Model used**: `gemini-3.6-flash` (flash tier, to conserve pro-tier quota
  which was already exhausted on the free plan during this check).
- **Result**: **Accurate.** The model correctly transcribed all Kannada text,
  correctly paired it with the adjacent English text, and produced correct
  Kannada→English translations for every line (verified by manual review
  against what was rendered — see transcript preserved in this repo's session
  history). No hallucinated or dropped lines.
- **What this does and does NOT prove**:
  - DOES show: the key works, the multimodal call path in
    `app/gemini_client.py`/`app/ingestion.py` is architecturally sound, and
    Gemini has genuine Kannada reading ability on clean, well-rendered text.
  - Does NOT show: performance on an actual photographed/scanned physical
    document — real stamp paper, handwriting, phone-camera skew/glare, low
    resolution, multi-column layouts, or a scanning artifact-heavy PDF. Those
    are exactly the failure modes the original spike protocol (5-10 samples
    including 2+ poor-quality scans) exists to catch, and this ad hoc check
    used none of them.
- **Go/no-go call**: **Not yet a formal go.** This is a positive leading
  indicator that lowers risk, but the team should still run
  `run_ocr_spike.py` against at least one or two *real* photographed Kannada
  documents (a real rental agreement page is fine — doesn't need to be a
  sensitive one) before fully trusting this in front of judges. Budget 15-30
  minutes for this before the demo, not before general development — it is
  no longer the "day-1 blocker" it was when no key existed, since the
  underlying capability is now confirmed to exist.
- **Also confirmed**: outbound network access to
  `generativelanguage.googleapis.com` works from a standard dev machine, and
  the `google-genai==0.3.0` SDK pinned in `requirements.txt` is compatible
  with the current live API.
