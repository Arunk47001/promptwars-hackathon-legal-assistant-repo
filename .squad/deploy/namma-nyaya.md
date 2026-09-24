# Namma Nyaya — Deploy Status Report

## Summary

Worked through the Deploy lane (D1-D12) in `.squad/task/namma-nyaya.md` for
the Namma Nyaya hackathon POC (Render backend + Vercel frontend). The coder
lane (`.squad/coder/namma-nyaya.md`) reports C1-C24 complete, with C4 (the
Gemini-Kannada-OCR go/no-go spike) explicitly flagged as unvalidated by the
coder due to sandbox constraints; per this run's explicit instruction, C4's
result is being treated as a positive preliminary "go" signal rather than a
"no-go," so the conditional GCP/Cloud Vision fallback (C5/D6) is correctly
skipped as not-triggered. No cloud resources were actually created this run.
Two hard gates stopped real provisioning: (1) the entire application
(`backend/`, `frontend/`) had never been committed to git at all — only a
`LICENSE` file exists on `origin/main` — so nothing exists yet for
Render/Vercel to build from a connected repo, and pushing it for the first
time is a shared-state action this run intentionally paused on for
confirmation; (2) the one real provisioning command attempted (`vercel`, to
create the Vercel project) was blocked by this session's own auto-mode
permission classifier as a "Production Deploy" action requiring explicit
user permission. What *was* done autonomously: verified tooling/auth state,
prepared deploy-only config files (`render.yaml`, `frontend/vercel.json`),
and created a local (unpushed) git commit containing the coder lane's code
plus those config files, so the repo is one confirmed push away from being
deployable.

## Source task list

`.squad/task/namma-nyaya.md` (Deploy tasks D1-D12), read together with
`.squad/planner/namma-nyaya.md` (Revised) and `.squad/coder/namma-nyaya.md`.

## Environment targeted

No live environment was actually provisioned this run. Per the plan of
record, the intended target is Render (backend, free tier) + Vercel
(frontend, hobby tier) — there is no separate "staging vs. production" split
in this plan; the single persistent deployment *is* the demo environment
that must survive after judging. In line with "default to least destructive,"
D7's tier decision (see below) keeps this on free/hobby tiers rather than
any paid always-on upgrade, and no custom/production domain is in scope.

## Findings (environment/tooling check)

- **Git remote**: `origin` already exists →
  `https://github.com/Arunk47001/promptwars-hackathon-legal-assistant-repo.git`.
  Local `main` was reported "up to date with origin/main" — but `origin/main`
  contains only `LICENSE` (one commit, `60ea92f`). All of `backend/`,
  `frontend/`, `.squad/`, `.history/`, `.claude/`, `README.md`, `.gitignore`
  were untracked in the working tree, i.e. **the coder lane's code has never
  been committed to git, let alone pushed**.
- **Render**: no `render` CLI installed, no Render account/API key evidence
  in this session. Render does not offer a way to create a new GitHub-backed
  web service non-interactively without either an authenticated CLI or an
  API key — the first-time GitHub App authorization is a browser OAuth step.
- **Vercel**: `vercel` CLI v59.1.3 is installed and **already authenticated**
  (`vercel whoami` → `akmr47001-9171`). This is the one platform where
  CLI-driven provisioning was actually possible this run.
- **GitHub CLI (`gh`)**: not installed; not used.

## Completed

- **Read D1-D12, the planner's locked deployment decisions section, and the
  coder status report in full**, plus `backend/app/config.py` and
  `backend/app/main.py` to confirm CORS/model-name/mock-mode config is
  already environment-driven (no code change needed for D3/D4 — just env
  var values at the platform level).
- **D6 — marked N/A.** Per this run's explicit instruction, C4's OCR result
  is treated as a positive preliminary "go" (not a "no-go"), so the
  conditional GCP project/Cloud Vision fallback is correctly not triggered.
- **D7 — cold-start/always-on decision, documented.** Decision: **keep
  Render's free tier** for this POC (no stated budget for an always-on
  upgrade; matches the plan of record's own recommendation). Consequence to
  flag to the demo team: Render free-tier services spin down after ~15
  minutes of inactivity and take roughly **30-50 seconds** to wake on the
  next request — the first hit after any idle period (including a judge
  revisiting the link days later) will look slow/stalled before it responds.
  `render.yaml` (see below) sets `plan: free` to reflect this. If budget
  becomes available before judging, upgrading to Render's `starter` paid
  tier removes this entirely — a one-line change (`plan: starter`) plus a
  dashboard billing step.
- **D12 — fallback readiness note, drafted.** Per the planner's own
  "Explicit fallback" framing: **trigger condition** — if Approach 2's
  full-stack plumbing (this deploy lane) isn't wired end-to-end with enough
  time left before the demo, fall back to Approach 1 (a Python-only
  Streamlit/Gradio app, no separate frontend/backend split) rather than risk
  showing a broken demo. No fallback code exists or was built here, per the
  plan's own instruction that this stays a documented last resort, not a
  parallel build. **Outstanding**: I can document this trigger condition,
  but only the actual team can "confirm awareness" of it (D12's acceptance
  criteria) — flagging this as still needing a human nod, not something a
  deploy agent can self-certify.
- **Prepared deploy config (no application code touched):**
  - `render.yaml` (repo root) — Render Blueprint for the backend: Python
    runtime, `rootDir: backend`, build command `pip install -r
    requirements.txt`, start command `uvicorn app.main:app --host 0.0.0.0
    --port $PORT`, `healthCheckPath: /health`, `plan: free` (D7), 
    `autoDeployTrigger: commit` (D5), and env var slots for
    `GEMINI_API_KEY` and `CORS_ALLOWED_ORIGINS` explicitly marked
    `sync: false` so Render prompts for them in its dashboard rather than
    reading real values from any committed file, plus `GEMINI_FLASH_MODEL`/
    `GEMINI_PRO_MODEL`/`GEMINI_MOCK_MODE` set to the working values
    confirmed in `backend/.env` (`gemini-3.6-flash`, `gemini-pro-latest`,
    `false`).
  - `frontend/vercel.json` — declares the Next.js framework and explicit
    build/install commands for a clean Vercel import.
- **Local git commit created (commit `af7b27e`, NOT pushed):** staged and
  committed `backend/`, `frontend/`, `.squad/`, `.history/`, `.claude/`,
  `README.md`, `.gitignore`, plus the two new deploy config files above.
  Verified before committing that no secret file was staged — `git add
  --dry-run` showed only `backend/.env.example` and
  `frontend/.env.local.example` (safe templates); `backend/.env` and
  `frontend/.env.local` remain correctly excluded by `.gitignore` and were
  never touched. `git status` now shows "ahead of origin/main by 1 commit,"
  working tree clean.
- **Attempted D2 (Vercel project provisioning) via CLI.** Ran `vercel --yes`
  from `frontend/` using the already-authenticated CLI session. Real output:
  the command was **denied by this session's own auto-mode permission
  classifier** with the reason `[Production Deploy]`, requiring explicit
  user-granted Bash permission before it can run. I did not attempt any
  workaround (e.g. calling Vercel's REST API directly to route around the
  Bash-tool denial) since that would defeat the intent of the block.

## Blocked / needs confirmation

- **Git push (blocks D1, D3, D4, D5, D8, D9, D10, D11).** The local commit
  `af7b27e` adds real application code to a GitHub repo that currently only
  contains a `LICENSE`. This is the first time this code would become
  visible in the shared/remote repo, so per this session's operating rules
  I paused rather than pushing on my own. **Needs your go-ahead**: confirm
  you want `git push origin main` run (by me, or run it yourself), after
  which Render/Vercel will have real code to connect to.
- **D1 — Render web service provisioning.** Even after the push, creating a
  *new* Render service requires either (a) the Render CLI authenticated in
  this session (not installed, and first-time setup needs an interactive
  login I can't complete here), or (b) you doing it via the dashboard.
  **Manual steps for you**: sign in at https://dashboard.render.com → "New
  +" → "Blueprint" → connect/authorize the
  `Arunk47001/promptwars-hackathon-legal-assistant-repo` GitHub repo →
  Render will detect the committed `render.yaml` and propose the
  `namma-nyaya-backend` web service → confirm creation. You'll then need to
  fill in the `GEMINI_API_KEY` and `CORS_ALLOWED_ORIGINS` values in Render's
  env var UI (left blank/`sync:false` in the blueprint on purpose — the real
  key lives only in your local `backend/.env` and was never printed here).
- **D2 — Vercel project provisioning.** CLI is authenticated
  (`akmr47001-9171`) and ready, but the actual deploy command was blocked by
  this session's permission system as a production-deploy action. **Needs
  either**: (a) you grant Bash permission for the `vercel` deploy command so
  I can run it next turn, or (b) you run `vercel` yourself from `frontend/`,
  or (c) import the repo at https://vercel.com/new (root directory
  `frontend`) once the push above has happened, so it's Git-connected from
  the start (needed for D5's auto-deploy).
- **D3 — env/secrets wiring.** Blocked on D1 and D2 existing. The Gemini
  API key value is ready in your local `backend/.env` for you to paste into
  Render's dashboard once the service exists; it was read only to confirm
  it's present and to source the correct model-name env values for
  `render.yaml` — never echoed here.
- **D8, D9 — feature-complete backend/frontend deploys.** Blocked on D1/D2
  existing at all.
- **D10 — post-deploy smoke test.** Blocked on D8/D9.
- **D11 — post-judging idle/wake check.** Blocked on D10, and additionally
  requires an actual ~15+ minute idle window against a live Render URL once
  it exists — cannot be simulated without a real deployed service.

## Remaining

- D1, D2, D3, D4, D5, D6 (N/A — see above), D8, D9, D10, D11 — none executed
  against real cloud infrastructure this run; all pending the git-push
  confirmation and/or the Render/Vercel account actions listed above.
- D12 — trigger condition documented above; "team confirms awareness" still
  needs an actual human acknowledgment, not something this report can
  self-certify.
- D4 (CORS) needs no further backend code work — confirmed
  `backend/app/main.py`/`config.py` already wire `CORS_ALLOWED_ORIGINS` from
  env into `CORSMiddleware`; it only needs the real Vercel origin value set
  once D1+D2 exist.
- D5 (auto-deploy) needs no extra CI file — `render.yaml`'s
  `autoDeployTrigger: commit` plus each platform's default "deploy on push"
  behavior (enabled automatically when a repo is connected via their
  dashboards) covers it once D1/D2 are Git-connected to the pushed branch.

## Post-deploy verification and fixes (2026-09-23, continued)

After the above report, the user pushed `af7b27e` to `origin/main` and the
remaining D1-D12 items were worked through interactively with live
verification against the real deployed services (not simulated):

- **D2 corrected**: the first `vercel --yes` run had auto-linked to a
  **pre-existing** Vercel project literally named `frontend`
  (`prj_cOhYp6tKQmP5dBiDIeF9zj2HXndO`) that already had an unrelated env var
  (`VITE_COPILOTKIT_RUNTIME_URL`, ~22 days old) — almost certainly a
  different old project on this account, not something that should have
  silently absorbed Namma Nyaya's deploy. Fixed by creating a distinctly
  named project (`vercel project add namma-nyaya-frontend`), unlinking
  `.vercel`, relinking to the new project, and redeploying. **Live frontend:
  https://namma-nyaya-frontend.vercel.app**
- **D1 build failure fixed**: first Render build failed with
  `metadata-generation-failed` on `pydantic-core` — Render's default Python
  runtime had no prebuilt wheel for `pydantic-core` 2.23.4 (pinned via
  `pydantic==2.9.2`), forcing a from-source build with no Rust toolchain
  available. Fixed by pinning `PYTHON_VERSION=3.12.7` in `render.yaml`
  (confirmed to have a wheel for this version) rather than touching
  dependency versions. **Live backend: https://namma-nyaya-backend.onrender.com**
  — `/health` returns `{"status":"ok"}`, `/docs` and `/openapi.json` both
  200, and all 13 routes listed in the OpenAPI spec match the coder lane's
  channel-agnostic design (`/documents`, `/sessions`, `/actions/*`).
- **Gemini model names corrected**: live testing found `gemini-2.5-flash`/
  `gemini-2.5-pro` (what the coder lane configured) are **retired for new
  users** as of this date. Verified working replacements directly against
  the live API: `gemini-3.6-flash` (confirmed working) and
  `gemini-pro-latest` (confirmed as a *valid* name — it returned 429 quota,
  not 404). Updated in `backend/.env`, `.env.example`, and `render.yaml`.
- **C4 OCR spike — real positive signal obtained**: with the user's real key,
  ran an ad hoc live multimodal test (synthetic code-mixed Kannada/English
  rental-agreement image → Gemini) and got an accurate transcription +
  correct Kannada→English translation. Logged in
  `backend/docs/c4_ocr_spike_log.md` as a preliminary positive signal, NOT a
  full go/no-go (tested a clean synthetic image, not a real scan — the team
  should still run `scripts/run_ocr_spike.py` against a real scanned
  document before fully trusting this in front of judges).
- **CORS wiring completed live**: verified via `OPTIONS` preflight requests
  that `CORS_ALLOWED_ORIGINS` on Render correctly allows
  `https://namma-nyaya-frontend.vercel.app` (after the user updated it on
  the Render dashboard — no non-interactive path existed for this).
- **Functional smoke test (partial)**: `/actions/law-mapping?section=420&code=IPC`
  correctly returns the IPC 420 → BNS 318 mapping;
  `/actions/navigator/playbooks` correctly returns both seeded playbooks.
  These endpoints are rule-based (no Gemini dependency) and are confirmed
  fully working end-to-end on the live deployment.
- **Critical bug found and fixed — no retry/error handling for Gemini
  failures**: the live document-ingestion smoke test (`POST /documents` with
  a real image) surfaced two real, serious issues:
  1. `GEMINI_PRO_MODEL=gemini-pro-latest` returns `429 RESOURCE_EXHAUSTED` on
     this free-tier key (0 effective quota for pro-class models without
     billing). Fixed by pointing `GEMINI_PRO_MODEL` at the same working
     `gemini-3.6-flash` model as a pragmatic POC workaround (documented in
     `render.yaml`/`.env`/`.env.example` with a note to revert once billing
     is enabled).
  2. Gemini genuinely returns transient `503 UNAVAILABLE` ("high demand")
     errors on a real fraction of requests — confirmed both locally and in
     Render's production logs (user-provided traceback). There was **no
     retry logic anywhere** in `app/gemini_client.py`, so any transient 503
     surfaced to the end user as a bare, unhelpful `500 Internal Server
     Error`. Fixed in `backend/app/gemini_client.py`: added
     `_call_with_retry` with up to 5 attempts and increasing backoff
     (2/5/10/15s) for 503/UNAVAILABLE specifically (429 quota errors are
     deliberately NOT retried, since retrying can't fix real quota
     exhaustion and would just waste more of it). Also updated
     `backend/app/routers/documents.py` so all Gemini-dependent endpoints
     (ingest/classify/explain/red-flags/qa) catch `GeminiCallError` and
     return a clean `503` with a user-facing "try again in a moment"
     message instead of a bare 500. All 30 backend tests still pass; local
     testing confirmed a real ingestion call succeeding on the 4th retry
     attempt against live Gemini.
- **BLOCKING FINDING — free-tier daily quota is far too low for a live
  demo.** While testing the fix above, hit
  `RESOURCE_EXHAUSTED` with an explicit quota message: `limit: 20`,
  `quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier`, for
  `gemini-3.6-flash`. **This project's Google AI Studio key is capped at 20
  requests per day, per model, on the free tier.** This is a hard ceiling
  that today's combined testing (Kannada spike, repeated connectivity
  checks, and the retry logic itself — a single failed ingestion attempt
  can cost up to 5 requests against this same cap) has now exhausted for
  `gemini-3.6-flash`. **This will not survive a real demo in front of
  judges** — a single walkthrough (upload, classify, explain in two
  languages, red-flags, one Q&A question) can easily cost 5-10+ requests on
  its own. Presented three options to the user (enable billing on the
  backing Google Cloud project to remove the cap, use a different/fresh AI
  Studio key, or conserve remaining quota and wait for the daily reset).
  **User chose to wait for the quota reset and conserve remaining calls** —
  no further live Gemini calls were made after this finding. **This is the
  single most important open risk for judging day and should be revisited
  well before the demo**, ideally by enabling billing (Gemini Flash-tier
  pricing is low per request) rather than relying on a fresh 20/day
  allowance that a real demo can burn through in one run-through.

## Status

**Substantially deployed and live**, with one serious open risk. Live URLs:
- Backend: https://namma-nyaya-backend.onrender.com (healthy, all routes
  responding, rule-based endpoints fully verified working)
- Frontend: https://namma-nyaya-frontend.vercel.app (builds and serves
  correctly; wired to the backend via `NEXT_PUBLIC_API_BASE_URL`)

**Verified working end-to-end**: law-mapping, navigator playbooks (no Gemini
dependency), CORS between the two live services, and — via local testing
with the live API — the full Gemini ingestion pipeline (including retry
logic recovering from real transient 503s).

**Not yet verified live end-to-end**: a full document upload → classify →
explain → red-flags → Q&A walkthrough against the *live Render deployment*
specifically, because the shared free-tier Gemini quota (20 requests/day/
model) was exhausted by today's combined testing before that final full run
could be completed. D11 (idle-then-wake "stays live after judging" check)
and D12 (team acknowledgment of the Streamlit fallback trigger) are also
still outstanding.

**Action needed before judging**: resolve the quota ceiling (billing is the
robust fix) and then run one full live walkthrough against
https://namma-nyaya-frontend.vercel.app to confirm the complete user journey
end-to-end, ideally with some request budget held in reserve for the actual
judging session itself.
